from urllib.parse import *
import time

def transcode(srcFile):
    try:
        from pathlib import Path
        from PIL import Image
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        if ext in [".jpg", ".png", ".jpeg", ".bmp"]:
            image = Image.open(srcFile, "r")
            format = image.format
            if format.lower() != "webp":
                fname = Path(srcFile).name
                newFile = srcFile.replace(fname[fname.index("."):], ".webp")
                image.save(newFile, "webp", quality=90)
                image.close()
                return True, newFile
    except Exception as e:
        pass
    return False, srcFile

def additionalUrl(srcFile, ossUrl):
    from pathlib import Path
    from PIL import Image
    try:
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        params = {}
        if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
            img = Image.open(srcFile)
            params["width"] = img.width
            params["height"] = img.height
        elif ext in [".mp4",".mov",".avi",".wmv",".mpg",".mpeg",".rm",".ram",".flv",".swf",".ts"]:
            params = {}
        elif ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
            params = {}
        else:
            params = {}
        parsed_url = urlparse(ossUrl)
        updated_query_string = urlencode(params, doseq=True)
        final_url = parsed_url._replace(query=updated_query_string).geturl()
        return final_url
    except:
        return ossUrl

def upload(src, taskUUID=None, needTranscode=False, keepItAlways=False, additionalUrl=False, uploadPath=None):
    import os
    from pathlib import Path
    from ryry import taskUtils as ryry_taskUtils
    if os.path.exists(src) == False:
        raise Exception(f"upload file not found")
    targetDomain = None
    if taskUUID == None or len(taskUUID) <= 0:
        taskUUID, taskInfo = ryry_taskUtils.taskInfoWithFirstTask()
        if taskInfo:
            targetDomain = taskInfo.get("domain", None)
    else:
        taskInfo = ryry_taskUtils.taskInfoWithUUID(taskUUID)
        if taskInfo:
            targetDomain = taskInfo.get("domain", None)
        if targetDomain == None or len(targetDomain) <= 0:
            from mecord import taskUtils as mecord_taskUtils
            uuid_has_country_info = mecord_taskUtils.taskCountryWithUUID(taskUUID)
            if uuid_has_country_info:
                #这里不区分meco还是mecord，请求meco/mecord后端接口时，根据本地状态来向不同服务器请求
                targetDomain = "https://m.mecoai.cn/" 

    needDeleteSrc = False
    if needTranscode:
        needDeleteSrc, newSrc = transcode(src)
    else:
        newSrc = src
    
    # 根据targetDomain判断使用不同的上传逻辑
    ossurl = uploadByDomain(newSrc, targetDomain, taskUUID, 
                            keepItAlways=keepItAlways, 
                            uploadPath=uploadPath,
                            needTranscode=needTranscode,
                            additionalUrl=additionalUrl)
        
    if additionalUrl:
        ossurl = additionalUrl(newSrc, ossurl)
    if needDeleteSrc:
        os.remove(newSrc)
    return ossurl

def uploadByDomain(src, targetDomain, taskUUID, keepItAlways=False, uploadPath=None, needTranscode=False, additionalUrl=False):
    import os
    from pathlib import Path
    import uuid
    from urllib.parse import urlparse
    
    file_name = Path(src).name
    ext = os.path.splitext(file_name)[-1][1:]
    
    parsed_domain, upload_path = parseDomainAndPath(targetDomain)
    if uploadPath:
        upload_path = uploadPath
    if isMecordConfig(parsed_domain):
        from mecord import upload as mecord_upload
        return mecord_upload.upload(src, taskUUID, 
                                    needTranscode=needTranscode, 
                                    needAddtionUrl=True) #mecord会使用签名信息，强制needAddtionUrl
    
    oss_config = getOssConfig(parsed_domain)
    if oss_config:
        new_file_name = ''.join(str(uuid.uuid4()).split('-'))
        return uploadToOss(src, f"{new_file_name}.{ext}", oss_config, upload_path)
    
    ftp_config = getFtpConfig(parsed_domain)
    if ftp_config:
        return ftpUpload(src, file_name, ftp_config, upload_path)
    
    if upload_path:
        if "mnt/NAS/mcn" in upload_path or "aigc_output/" in upload_path:
            ftp_config = getFtpConfig("219.136.123.179")
            return ftpUpload(src, file_name, ftp_config, upload_path)
        elif (targetDomain != None and"aigc_output/" in targetDomain):
            ftp_config = getFtpConfig("219.136.123.179")
            return ftpUpload(src, file_name, ftp_config, upload_path)
        elif (targetDomain == None or len(targetDomain) <= 0) and (uploadPath and len(uploadPath) > 0):
            #找不到domain，但是有uploadPath的情况下，默认走ftp
            ftp_config = getFtpConfig("219.136.123.179")
            return ftpUpload(src, file_name, ftp_config, upload_path)
       
    from ryry import ryry_webapi
    return ryry_webapi.upload(src, ext, 
                              keepItAlways=keepItAlways, 
                              needTranscode=needTranscode, 
                              additionalUrl=additionalUrl)

def parseDomainAndPath(targetDomain):
    from urllib.parse import urlparse
    
    if not targetDomain:
        return "", ""
    
    if targetDomain.startswith(('http://', 'https://', 'ftp://')):
        parsed = urlparse(targetDomain)
        domain = parsed.netloc
        path = parsed.path.lstrip('/')
        return domain, path
    
    if '/' in targetDomain:
        parts = targetDomain.split('/', 1)
        domain = parts[0]
        path = parts[1]
        return domain, path
    
    return targetDomain, ""

def uploadToOss(file, new_file_name, oss_config, upload_path=""):
    import hashlib
    import hmac
    import base64
    import datetime
    import requests
    
    bucket = oss_config["bucket"]
    endpoint = oss_config["endpoint"]
    key_id = utils._decode_key(utils.K1)
    key_secret = utils._decode_key(utils.K2)
    
    timestamp = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")        
    content_type = "application/octet-stream"
    
    if upload_path:
        upload_path = upload_path.strip('/')
        object_key = f"{upload_path}/{new_file_name}"
    else:
        object_key = f"temp/{new_file_name}"
    
    resource = f"/{bucket}/{object_key}"
    string_to_sign = f"PUT\n\n{content_type}\n{timestamp}\n{resource}"    
    signature = base64.b64encode(
        hmac.new(key_secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1).digest()
    ).decode('utf-8')        
    
    url = f"https://{bucket}.{endpoint}/{object_key}"
    headers = {
        "Date": timestamp,
        "Authorization": f"OSS {key_id}:{signature}",
        "Content-Type": content_type
    }
    
    with open(file, "rb") as f:
        file_data = f.read()
    
    response = requests.put(url, data=file_data, headers=headers)
    if response.status_code == 200:
        return f"{oss_config['domain']}/{object_key}"
    else:
        raise Exception(f"OSS upload failed: {response.status_code}")

def deepFtpUpload(file, new_file_name, ftp, writepath, readpath):
    try:
        safe_cwd(ftp, writepath)
    except:
        safe_mkd(ftp, writepath)
        safe_cwd(ftp, writepath)
            
    with open(file, 'rb') as f:
        ftp.storbinary(f'STOR {new_file_name}', f)
    return f"{readpath}/{writepath}/{new_file_name}"

def ftpUpload(file, new_file_name, subdomain, upload_path=""):
    ip = subdomain["host"]
    port = subdomain["port"]
    username = subdomain["username"]
    password = subdomain["password"]
    writepath = subdomain["writepath"]
    readpath = subdomain["readpath"]
    retry = 0
    import ftplib
    while retry < 3:
        try:
            if retry > 0:
                has_bak = FTP_REPLACEMENT.get(ip, None)
                if has_bak:
                    bak_config = DOMAIN_CONFIG.get(has_bak, None)["config"]
                    ftp = ftplib.FTP()
                    ftp.connect(bak_config["host"], bak_config["port"], timeout=5)
                    ftp.login(bak_config["username"], bak_config["password"])  
                    if upload_path:
                        if upload_path[0:1] == "/":
                            upload_path = upload_path[1:]
                        if "mnt/NAS/mcn/" in upload_path:
                            upload_path = upload_path.replace("mnt/NAS/mcn/", "")
                        s = deepFtpUpload(file, new_file_name, ftp, upload_path, readpath)
                    else:
                        s = deepFtpUpload(file, new_file_name, ftp, writepath, readpath)
                    
                    ftp.quit()
                    return s

            ftp = ftplib.FTP()
            ftp.connect(ip, port, timeout=5)
            ftp.login(username, password)  

            if upload_path:
                if upload_path[0:1] == "/":
                    upload_path = upload_path[1:]
                if "mnt/NAS/mcn/" in upload_path:
                    upload_path = upload_path.replace("mnt/NAS/mcn/", "")
                s = deepFtpUpload(file, new_file_name, ftp, upload_path, readpath)
            else:
                s = deepFtpUpload(file, new_file_name, ftp, writepath, readpath)
            
            ftp.quit()
            return s
        except:
            time.sleep(5)
        finally:
            retry+=1
    raise Exception("uplad fail!")
    
def _can_connect_ftp(ip, port, username, password, writepath):  
    import ftplib
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, port, timeout=5)
        ftp.login(username, password)  
        try:
            safe_cwd(ftp, writepath)
        except:
            safe_mkd(ftp, writepath)
            safe_cwd(ftp, writepath)
        ftp.quit()
        return True
    except Exception as e:  
        print(f"Failed to connect to FTP server {ip}:{writepath} {e}")  
        return False

# FTP配置
ftp_192_168_50_12={
    "host" : "192.168.50.12",
    "port": 21,
    "username" : "mcn",
    "password" : "meco@2024+",
    "writepath" : "cache",
    "readpath" : "ftp://219.136.123.179/mnt/NAS/mcn"
}
ftp_219_136_123_179={
    "host" : "219.136.123.179",
    "port": 2221,
    "username" : "mcn",
    "password" : "meco@2024+",
    "writepath" : "cache",
    "readpath" : "ftp://219.136.123.179/mnt/NAS/mcn"
}

from ryry import utils
oss_res_config = {
    "bucket": "p-res-gz",
    "endpoint": "oss-cn-guangzhou.aliyuncs.com",
    "domain": "https://res.zjtemplate.com"
}

oss_upload_config = {
    "bucket": "p-upload-gz",
    "endpoint": "oss-cn-guangzhou.aliyuncs.com",
    "domain": "https://upload.zjtemplate.com"
}

oss_template_config = {
    "bucket": "p-template-hk",
    "endpoint": "oss-cn-hongkong.aliyuncs.com",
    "domain": "https://oss.zjtemplate.com"
}

def match_wildcard_domain(target_domain, pattern):
    if pattern.startswith("*."):
        suffix = pattern[1:]  # 去掉 "*." 前缀
        return target_domain.endswith(suffix)
    return target_domain == pattern

def get_domain_config(target_domain):
    # 首先尝试精确匹配
    if target_domain in DOMAIN_CONFIG:
        return DOMAIN_CONFIG[target_domain]
    
    # 然后尝试通配符匹配
    for pattern, config in DOMAIN_CONFIG.items():
        if match_wildcard_domain(target_domain, pattern):
            return config
    
    return None

DOMAIN_CONFIG = {
    "192.168.50.12": {"type": "ftp", "config": ftp_192_168_50_12},
    "219.136.123.179": {"type": "ftp", "config": ftp_219_136_123_179},
    "183.6.90.205": {"type": "ftp", "config": ftp_219_136_123_179},
    "ftp://192.168.50.12/mnt/NAS/mcn/cache": {"type": "ftp", "config": ftp_192_168_50_12},
    "ftp://183.6.90.205/mnt/NAS/mcn/cache": {"type": "ftp", "config": ftp_219_136_123_179},
    "ftp://219.136.123.179/mnt/NAS/mcn/cache": {"type": "ftp", "config": ftp_219_136_123_179},
    "res.zjtemplate.com": {"type": "oss", "config": oss_res_config},
    "upload.zjtemplate.com": {"type": "oss", "config": oss_upload_config},
    "oss.zjtemplate.com": {"type": "oss", "config": oss_template_config},
    "*.mecoai.cn": {"type": "mecord-cli", "config": {}},
    "*.mecordai.com": {"type": "mecord-cli", "config": {}},
}

FTP_REPLACEMENT = {
    "192.168.50.12": "219.136.123.179",
    "219.136.123.179": "192.168.50.12",
    "183.6.90.205": "219.136.123.179",
}

SUBDOMAIN = {
    "183.6.90.205": [
        ftp_192_168_50_12,
        ftp_219_136_123_179,
    ],
    "219.136.123.179": [
        ftp_192_168_50_12,
        ftp_219_136_123_179,
    ],
    "192.168.50.12": [
        ftp_192_168_50_12,
        ftp_219_136_123_179,
    ]
}

def getOssConfig(targetDomain):
    config = get_domain_config(targetDomain)
    if config and config["type"] == "oss":
        return config["config"]
    return None

def isMecordConfig(targetDomain):
    config = get_domain_config(targetDomain)
    if config and config["type"] == "mecord-cli":
        return True
    return False

def getFtpConfig(targetDomain):
    config = get_domain_config(targetDomain)
    if config and config["type"] == "ftp":
        return config["config"]
    return None

def getSubdomain(targetDomain):
    if len(targetDomain) <= 0:
        return None
    
    ftp_config = getFtpConfig(targetDomain)
    if ftp_config:
        if _can_connect_ftp(ftp_config["host"], ftp_config["port"], ftp_config["username"], ftp_config["password"], ftp_config["writepath"]):
            return ftp_config
    
    for ip in SUBDOMAIN.keys():
        for host_item in SUBDOMAIN[ip]:
            if targetDomain == host_item["readpath"]:
                if _can_connect_ftp(ip, host_item["port"], host_item["username"], host_item["password"], host_item["writepath"]):
                    return host_item
    return None

def getFirstSupportSubdomain():
    def get_network_hash():
        import socket
        from hashlib import md5
        try:
            local_ip = socket.gethostbyname('localhost')
        except socket.gaierror:
            local_ip = '127.0.0.1'  # 默认回退到 localhost 地址
        return md5(local_ip.encode('utf-8')).hexdigest()
    network_hash = get_network_hash()  
    def _getFirstSupportSubdomain():
        for domain, config in DOMAIN_CONFIG.items():
            if config["type"] == "oss":
                return {"type": "oss", "config": config["config"], "domain": config["config"]["domain"]}
            if config["type"] == "mecord-cli":
                # 对于通配符域名，返回一个示例域名
                if domain.startswith("*."):
                    # 将 *.mecoai.cn 转换为 example.mecoai.cn
                    example_domain = "example" + domain[1:]
                    return {"type": "mecord-cli", "config": {}, "domain": example_domain}
                else:
                    return {"type": "mecord-cli", "config": {}, "domain": domain}
            elif config["type"] == "ftp":
                ftp_config = config["config"]
                if _can_connect_ftp(ftp_config["host"], ftp_config["port"], ftp_config["username"], ftp_config["password"], ftp_config["writepath"]):
                    return {"type": "ftp", "config": ftp_config, "domain": ftp_config["readpath"]}
        
        for ip in SUBDOMAIN.keys():
            for host_item in SUBDOMAIN[ip]:
                if _can_connect_ftp(ip, host_item["port"], host_item["username"], host_item["password"], host_item["writepath"]):
                    return {"type": "ftp", "config": host_item, "domain": host_item["readpath"]}
        return None
    from ryry import store
    sp = store.Store()
    read_data = sp.read()
    firstSupportDomainConfig = read_data.get("firstSupportDomainConfig", {})
    if len(firstSupportDomainConfig.keys()) < 1:
        firstSupportDomainConfig = _getFirstSupportSubdomain()
        if firstSupportDomainConfig:
            firstSupportDomainConfig["hash"] = network_hash
            read_data["firstSupportDomainConfig"] = firstSupportDomainConfig
            sp.write(read_data)
    else:
        last_network_hash = firstSupportDomainConfig.get("hash", "")
        #网络变化，或者旧版本数据的时候，重新更新
        if last_network_hash != network_hash or "domain" not in firstSupportDomainConfig:
            firstSupportDomainConfig = _getFirstSupportSubdomain()
            if firstSupportDomainConfig:
                firstSupportDomainConfig["hash"] = network_hash
                read_data["firstSupportDomainConfig"] = firstSupportDomainConfig
                sp.write(read_data)
    return firstSupportDomainConfig

def download(url, saveDir):
    import uuid, requests, os
    from urlparser import urlparser
    from fake_useragent import UserAgent
    if len(url) <= 0:
        return None
    try:
        name = ''.join(str(uuid.uuid4()).split('-'))
        
        if url.startswith("ftp"):
            import ftplib, random
            parsed_url = urlparse(url)  
            host = parsed_url.hostname
            if host in SUBDOMAIN:
                for host_item in SUBDOMAIN[host]:
                    try:
                        ip = host_item["host"]
                        port = host_item["port"]
                        username = host_item["username"]
                        password = host_item["password"]
                        writepath = host_item["writepath"]
                        readpath = host_item["readpath"]
                        replace_path = host_item.get("path_replace", [])
                        ftp = ftplib.FTP()
                        ftp.connect(ip, port, timeout=5)
                        ftp.login(username, password)
                    
                        if len(replace_path) > 0:
                            parsed_url = urlparse(url.replace(replace_path[0], replace_path[1]))
                        remote_filepath = parsed_url.path
                        if "." in urlparser.urlparse(url).path:
                            ext = urlparser.urlparse(url).path[urlparser.urlparse(url).path.index("."):]
                            savePath = os.path.join(saveDir, f"{name}{ext}")
                            with open(savePath, 'wb') as f:  
                                ftp.retrbinary(f'RETR {remote_filepath}', f.write)
                            return savePath
                        else:
                            safe_cwd(ftp, remote_filepath)
                            files = ftp.nlst()
                            if files:
                                random_file = random.choice(files)
                                savePath = os.path.join(saveDir, f"{name}_{random_file}")
                                with open(savePath, 'wb') as f:  
                                    ftp.retrbinary(f'RETR {random_file}', f.write)  
                                return savePath
                        ftp.quit()
                    except Exception as ex:
                        pass
            print(f"download fail: domain {host} not support")
        elif url.startswith("http"):
            ua = UserAgent()
            ext = urlparser.urlparse(url).path[urlparser.urlparse(url).path.index("."):]
            savePath = os.path.join(saveDir, f"{name}{ext}")
            if os.path.exists(savePath):
                os.remove(savePath)
            
            parsed_url = urlparse(url)
            if parsed_url.netloc in ["res.zjtemplate.com", "upload.zjtemplate.com", "oss.zjtemplate.com"]:
                try:
                    file = requests.get(url, verify=False, 
                                        headers={'User-Agent': ua.random}, timeout=30)
                    with open(savePath, "wb") as c:
                        c.write(file.content)
                    if os.path.exists(savePath) and os.stat(savePath).st_size > 100:
                        return savePath
                except Exception as ex:
                    print(f"OSS download failed: {ex}")
                    pass
            
            #first orginal url
            try:
                file = requests.get(url, verify=False, 
                                    headers={'User-Agent': ua.random}, timeout=30)
                with open(savePath, "wb") as c:
                    c.write(file.content)
                if os.path.exists(savePath) and os.stat(savePath).st_size > 100:
                    return savePath
            except:
                pass
            
            try:
                parsed_url = urlparser.urlparse(url)
                domain_parts = parsed_url.netloc.split('.')
                if len(domain_parts) >= 3:
                    subdomain = domain_parts[0]  # 例如：upload、r2、widget等
                else:
                    subdomain = domain_parts[0]  # 默认处理
                #second, bak url
                file = requests.get(f"https://aigc.zjtemplate.com/{subdomain}{parsed_url.path}", 
                                    verify=False, 
                                    headers={
                                        'User-Agent': ua.random,
                                    },
                                    timeout=30)
                with open(savePath, "wb") as c:
                    c.write(file.content)
                if os.path.exists(savePath) and os.stat(savePath).st_size > 100:
                    return savePath
            except Exception as ex:
                print(ex)
                pass
                
            print(f"download success but file not found")
        else:
            print(f"url {url} not support")
    except Exception as e:
        print(f"download fail: {e}")
    return None

def safe_cwd(ftp, path):
    try:
        ftp.cwd(path)
        return
    except:
        pass
    
    if path[0:1] == "/":
        try:
            ftp.cwd(path.lstrip('/'))
            return
        except:
            pass
    else:
        try:
            ftp.cwd('/' + path)
            return
        except:
            pass
        
    if path[-1:] != "/":
        try:
            ftp.cwd(path + "/")
            return
        except:
            pass
    else:
        try:
            ftp.cwd(path.rstrip('/'))
            return
        except:
            pass
    raise Exception("cwd fail!")

def safe_mkd(ftp, path):
    try:
        ftp.mkd(path)
        return
    except:
        pass
    
    if path[0:1] == "/":
        try:
            ftp.mkd(path.lstrip('/'))
            return
        except:
            pass
    else:
        try:
            ftp.mkd('/' + path)
            return
        except:
            pass
        
    if path[-1:] != "/":
        try:
            ftp.mkd(path + "/")
            return
        except:
            pass
    else:
        try:
            ftp.mkd(path.rstrip('/'))
            return
        except:
            pass
    raise Exception("cwd fail!")

def downloadDir(url, saveDir, useCount=-1, autoDelete=False):
    import uuid, os
    if len(url) <= 0:
        return None
    try:
        name = ''.join(str(uuid.uuid4()).split('-'))
        
        if url.startswith("ftp"):
            import ftplib, random
            parsed_url = urlparse(url)  
            host = parsed_url.hostname
            if host in SUBDOMAIN:
                for host_item in SUBDOMAIN[host]:
                    try:
                        ip = host_item["host"]
                        port = host_item["port"]
                        username = host_item["username"]
                        password = host_item["password"]
                        replace_path = host_item.get("path_replace", [])
                        ftp = ftplib.FTP()
                        ftp.connect(ip, port, timeout=5)
                        ftp.login(username, password)   
                    
                        if len(replace_path) > 0:
                            parsed_url = urlparse(url.replace(replace_path[0], replace_path[1]))
                        remote_filepath = parsed_url.path
                        safe_cwd(ftp, remote_filepath)
                        files = ftp.nlst()
                        savePath = os.path.join(saveDir, f"{name}")
                        if os.path.exists(savePath) == False:
                            os.makedirs(savePath)
                        if useCount > 0 and useCount <= len(files):
                            files = random.sample(files, useCount)
                        for file in files:
                            with open(os.path.join(savePath, file), 'wb') as f:  
                                ftp.retrbinary(f'RETR {file}', f.write)
                            if autoDelete:
                                try:
                                    ftp.delete(file)
                                except Exception as e:
                                    print(f"Error deleting file {file}: {e}")
                        ftp.quit()
                        return savePath
                    except Exception as ex:
                        print(ex)
                        pass
            print(f"downloadDir fail: domain {host} not support")
        else:
            print(f"url {url} not support")
    except Exception as e:
        print(f"downloadDir fail: {e}")
    return None