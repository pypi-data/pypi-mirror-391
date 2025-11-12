# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 17:32:43 2019
Created on Python3.6.8
@author:
    liwancai
    QQ:248411282
"""
#%% 加载包
import shutil,os,json,csv,hashlib ,pickle,re
from liwancai.Functions.LOG import log
#==============================================================================
def GetthisPyPath(script_path = os.path.abspath(__file__)):# 获取当前脚本的路径):
    script_directory = os.path.dirname(script_path)# 获取当前脚本所在的目录
    relative_directory = os.path.relpath(script_directory)# 获取当前脚本所在的相对目录
    return  relative_directory
#%% 基础功能
def SplitDiv(path):
    '''分离盘符与路径'''
    import os
    drive,path=os.path.splitdrive(path)
    return drive,path
def SplitDir(path):
    '''文件路径和文件分离'''
    import os
    pathdir,filename=os.path.split(path)
    return pathdir,filename
def DirName(path):
    '''取路径中文件夹路径'''
    import os
    pathdir=os.path.dirname(path)
    return pathdir
def FileName(path):
    '''取路径中文件'''
    import os
    filename=os.path.basename(path)
    return filename
def FileEND(path):
    '''分离后缀名'''
    import os
    pathfile,endwith=os.path.splitext(path)
    return pathfile,endwith
#==============================================================================
def Mkdir(path):
    '''创建文件夹'''
    try:
        isExists = os.path.exists(path)  # 判断文件路径是否存在
        if not isExists:
            os.makedirs(path)
            log.Info("\n|■|文件夹==>> %s |■|创建成功|■|" % path)
        else:
            log.Info("\n|■|文件夹==>> %s |■|已经存在|■|" % path)
    except Exception as exception:
        log.Error(str(exception))
#==============================================================================
def FileSize(filepath):
    '''获取文件尺寸'''
    try:return os.path.getsize(filepath)/1024
    except Exception as exception:
        log.Error(str(exception))
#==============================================================================
def MoveTO(FilePath,Topath):
    '''移动文件到新的文件目录'''
    try:
        if os.path.exists(FilePath):# 如果文件存在
            Mkdir(Topath)#创建文件夹
            shutil.move(FilePath, Topath)   #复制文件
            log.Info('\n|■|文件: %s |■|移动成功|■|' % FilePath)
        else:log.Info('\n|■|文件: %s |■|不存在|■|' % FilePath)
    except Exception as exception:log.Error(str(exception))
#==============================================================================
def CopyTo(FilePath, Topath,force=False):
    try:
         if os.path.exists(FilePath):# 如果文件存在
            Mkdir(Topath)#创建文件夹
            dstFile= f"{Topath}/{FileName(FilePath)}"
            if  os.path.exists(dstFile) :
                if force: 
                    Del_F(dstFile)
                    log.Info('\n|■|文件: %s |■|已存在,强制复制|■|' % dstFile)
                else:return log.Info('\n|■|文件: %s |■|已存在，跳过复制|■|' % dstFile)
            shutil.copy(FilePath, Topath)
            log.Info('\n|■|文件: %s |■|复制成功|■|' % FilePath)
    except FileNotFoundError:
        log.Error('\n|■|文件: %s |■|不存在|■|' % FilePath)
#==============================================================================
def ReName(srcFile,dstFile):
    '''文件重命名'''
    try:
        os.rename(srcFile,dstFile)
        log.Info(f"\n|■|源文件:{srcFile}==>>目标:{dstFile} 重命名成功|■|")
    except Exception as exception:
        log.Error(str(exception))
#==============================================================================
def Del_P(path):
    '''删除文件夹'''
    try:
        shutil.rmtree(path)
        log.Info('\n|■|文件夹: %s |■|删除成功|■|' % path)
    except Exception as exception:
        log.Error(str(exception))
def Del_F(filepath):
    '''删除文件'''
    try:
        if os.path.exists(filepath):  # 如果文件存在 # 删除文件,可使用以下两种方法。
            os.remove(filepath)
            log.Info('\n|■|文件: %s |■|删除成功|■|' % filepath)
        else:
            log.Info('\n|■|文件: %s |■|不存在|■|' % filepath)  # 则返回文件不存在
    except Exception as exception:
        log.Error(str(exception))
#==============================================================================
def Pathsdirs(path):
    '''路径下文件夹'''
    return [os.path.join(path, info) for info in os.listdir(path)]
def Pathsname(path):
    '''路径下文件夹名称'''
    return [info for info in os.listdir(path) if '.' not in info]
def Del_NanP(pathroot=None,endlist=[".csv",".CSV"]):
    '''文件夹下没有以endlist后缀结尾的文件，就删除文件夹'''
    if not pathroot:return
    paths=Pathsdirs(pathroot)
    for path in paths:
        files=EndWithPath(path, endlist)
        if len(files)<1:Del_P(path)
#==============================================================================
def SavePickle(ClassM, filename, PATH='./Datas/STDatas/'):
    '''保存状态'''
    log.Info("\n||保存状态(%s)...||"%(filename))
    Mkdir(PATH)
    Save = open("%s%s.pkl" % (PATH, filename), 'wb')
    myclass = pickle.dumps(ClassM)
    Save.write(myclass)
    Save.close()
    log.Info("\n||保存状态(%s)成功!! ||"%(filename))
def LoadPickle(filename, PATH='./Datas/STDatas/'):
    '''加载状态'''
    try:
        log.Info("\n||尝试加载状态==>> %s||"%(filename))
        with open("%s%s.pkl" % (PATH, filename), 'rb') as file:
            ClassM = pickle.loads(file.read())
        log.Info("\n||加载状态(%s)完成!! ||"%(filename))
        return ClassM
    except:
        log.Info("\n||状态(%s)为空...||"%(filename))
        return None
#==============================================================================
def WriteFile(data, filename, path, arge="a"):
    '''save text'''
    try:
        Mkdir(path)
        File = open(f"{path}{filename}", arge)  # 输出的txt文件路径
        File.write(data)
        File.close()
    except Exception as exception:log.Error(str(exception))
#==============================================================================
def ReadFile(filepath):
    '''读取任意文件'''
    with open(filepath, "r") as file: return file.read()
#==============================================================================
def ReadLine(filepath,encoding='utf-8'):
    '''按行读取文件'''
    with open(filepath,encoding=encoding) as file:return file.readlines()
#==============================================================================
def Save_Json(data, path='./', filename='filename',mode='w'):
    Mkdir(path)
    return (open('%s%s.json' % (path, filename), mode)).write(f"\n{json.dumps(data)}\n")
#==============================================================================
def Read_Json(filename,path, encoding='gb18030'):
    return json.loads((open('%s%s.json' % (path,filename), 'r', encoding=encoding)).read())
#==============================================================================
def Read_Csv(path, encoding='gb18030', chunksize=None,nrows=None, index_col=0,**arge):
    import pandas as pd
    if os.path.getsize(path)>0:#文件不为空
        return pd.read_csv( path,index_col=index_col, encoding=encoding,
                            nrows=nrows, chunksize=chunksize, engine='python',**arge)
    else: return pd.DataFrame()
#==============================================================================
def Read_xls(path):
    import pandas as pd
    return pd.read_excel(path)
#==============================================================================
def Save_csv(df, filepath, encoding='gb18030', mode=None,index=None):
    '''pandas df to csv'''
    import os
    try:
        isExists = os.path.exists(filepath)
        if mode == None:
            if not isExists:
                Mkdir(DirName(filepath))#创建对应文件夹
                mode, header = 'w', True
                df.to_csv(filepath, mode=mode, header=header, encoding=encoding,index=index)
                log.Info('\n|■|文件: %s |■|保存成功|■|' % filepath)
            else:
                mode, header = 'a', False
                df.to_csv(filepath, mode=mode, header=header, encoding=encoding,index=index)
                log.Info('\n|■|文件: %s |■|追加成功|■|' % filepath)
        else:
            header = False if "a" in mode else True
            df.to_csv(filepath, mode=mode, header=header, encoding=encoding,index=index)
            log.Info('\n|■|文件: %s |■|追加成功|■|' % filepath)
    except Exception as exception:
        log.Error(str(exception))
#==============================================================================
class TodoCsv:
    '''
    a:附加写,不可读。
    a+:附加读写。追加写。
    r:只读,最常用。不创建,不存在会报错。（读二进制文件可能会读取不全）
    rb:只读。二进制文件按二进制位进行读取。不创建,不存在会报错。
    rt:只读。文本文件用二进制读取。不创建,不存在会报错。
    r+:可读写。覆盖写。不创建,不存在会报错。
    w:只写。存在则覆盖。不存在则创建。
    w+:可读写。存在则覆盖。不存在则创建。
    '''
    def __init__(self,csvname,filepath,act="a+",encoding='gb18030',newline=''):
        Mkdir(filepath)
        self.pathfile=f"{filepath}{csvname}.csv"
        self.csvfile=open(self.pathfile,mode=act,encoding=encoding,newline=newline)
        self.csvfile_w=csv.writer(self.csvfile)
    def writer(self,csvdata):
        self.csvfile_w.writerow(csvdata)
    def flush(self):
        self.csvfile.flush()
    def close(self):
        self.csvfile.close()
    def GetSize(self):
        return os.path.getsize(self.pathfile) 
# #==============================================================================
# import tkinter   as tk
# from   tkinter   import filedialog
# class TK_file:
#     '''文件夹路径操作'''
#     def __init__(self):
#         self.root = tk.Tk()   # 创建一个Tkinter.Tk()实例
#         self.root.withdraw()  # 将Tkinter.Tk()实例隐藏
#     @classmethod
#     def OpenFile(cls,title="请选择一个文件",filetypes=[('All Files', ' *')]):
#         return filedialog.askopenfilename(title=title,filetypes=filetypes,defaultextension='.tif', multiple=True)
#     @classmethod
#     def OpenFiles(cls,title="请选择多个文件",filetypes=[('All Files', ' *')]):
#         return filedialog.askopenfilename(title=title,filetypes=filetypes)
#     @classmethod
#     def SaveFile(cls,title="请选择文件存储路径",filetypes=[('All Files', ' *')]):
#         return filedialog.askopenfilename(title=title,filetypes=filetypes, defaultextension='.tif')
#     @classmethod
#     def DirPath(cls,):
#         return filedialog.askdirectory(title='选择目标文件夹')
#     @classmethod
#     def SrePath(cls,):
#         return filedialog.askdirectory(title='选择源始文件夹')
# def SreTarDIR():  # 窗口选择文件夹路径
#     '''源文件夹 目标文件夹选择'''
#     try:
#         root = tk.Tk()
#         root.withdraw()
#         ###请选择源始文件夹
#         log.Info('\n|■|请选择源始文件夹|■|')
#         source_dir = filedialog.askdirectory(title='选择源始文件夹')
#         log.Info('\n|■|<<源始文件夹: %s >>|■|' % source_dir)
#         ###请选择目标文件夹
#         log.Info('\n|■|请选择目标文件夹|■|')
#         target_dir = filedialog.askdirectory(title='选择目标文件夹')
#         log.Info('\n|■|<<目标文件夹: %s >>|■|' % target_dir)
#         return source_dir,target_dir
#     except Exception as exception:
#         log.Error(str(exception))
#         return None, None
#==============================================================================
def ImgToBase64(filename,path):
    '''
    图片转base64
    '''
    import io
    from PIL import Image
    img=Image.open(f"{path}{filename}")
    try:r,g,b,a = img.split()  
    except: r,g,b = img.split() 
    img = Image.merge('RGB',(r,g,b))    
    output=io.BytesIO()
    img.save(output, format='JPEG')#
    strimg=Base64_img(output.getvalue())
    return  strimg
def Base64_img(img):
    '''base64编码'''
    import base64
    return str(base64.b64encode(img))[1:]
def Base64ImgSave(name,img_str,path="./temp/"):
    '''base64转图片'''
    import base64,time
    Mkdir(path)
    filename=f'{path}{name}{str(time.time())}.png'
    with open(filename, 'wb') as imgfile:
        imgfile.write(base64.b64decode(img_str))#base64解码
        imgfile.close()
        return os.path.abspath(filename)#发出文件绝对路径(用于微信推送)
#============================================================================== 
def RunCMD(cmd_string):
    """
    执行cmd命令，并得到执行后的返回值，python调试界面输出返回值
    :param cmd_string: cmd命令，如：'adb devices'
    :return:
    """
    import subprocess
    log.Info(f'运行cmd指令：{cmd_string}')
    return subprocess.Popen(cmd_string, shell=True, stdout=None, stderr=None).wait()

#============================================================================== 
def is_The_file(filename, Endlist=['.png', '.jpg', 'tif', 'TIF', '.jpeg', '.JPG', '.JPEG', '.PNG', '.gif', '.GIF']):
    '''
    判断指定后缀名文件:如
    图片 ['.png', '.jpg','tif','TIF', '.jpeg', '.JPG', '.JPEG', '.PNG','.gif','.GIF']
    文档 ['.pdf','.PDF','.csv','.CSV','.doc','.docx','.xls','.DOC','.DOCX','.XLS','.XLSX','.xlsx']
    '''
    return any(filename.endswith(extension) for extension in Endlist)
#==============================================================================
def Scan_File(list_name, path="./"):
    '''查找目录下所有文件'''
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        file_path = file_path.replace('\\', '/')
        if os.path.isdir(file_path):
            Scan_File(list_name, file_path)
        else:
            list_name.append(file_path)
    return  list_name
def EndWithPath(path, endlist):
    '''获取指定后缀名的文件路径'''
    try:
        list_name = []
        Scan_File(list_name, path)
        return [x for x in list_name if is_The_file(x, endlist)]
    except Exception as exception:
        log.Error(str(exception))
        return []
#%% 哈希值获取
###############################################################################
###文件哈希基础构建
def file_hash(file_path: str,hash_method):
    if not os.path.isfile(file_path):return None
    h = hash_method()
    with open(file_path,'rb') as f:
        while True:
            b = f.read(8192)
            if not b:break	
            h.update(b)
    return h.hexdigest()
###############################################################################
def file_md5(file_path: str):
    return file_hash(file_path,hashlib.md5)
def file_sha256(file_path: str):
    return file_hash(file_path,hashlib.sha256)
def file_sha512(file_path: str):
    return file_hash(file_path,hashlib.sha512)
def file_sha384(file_path: str):
    return file_hash(file_path,hashlib.sha384)
def file_sha1(file_path: str):
    return file_hash(file_path,hashlib.sha1)
def file_sha224(file_path: str):
    return file_hash(file_path,hashlib.sha224)
###############################################################################
###字符串哈希基础构建
def str_hash(content: str,hash_method,encoding: str = 'UTF-8'):
    return hash_method(content.encode(encoding)).hexdigest()
###############################################################################
def str_md5(content: str,encoding: str = 'UTF-8'):
    return str_hash(content,hashlib.md5,encoding)
def str_sha256(content: str,encoding: str = 'UTF-8'):
    return str_hash(content,hashlib.sha256,encoding)
def str_sha512(content: str,encoding: str = 'UTF-8'):
    return str_hash(content,hashlib.sha512,encoding)
def str_sha384(content: str,encoding: str = 'UTF-8'):
    return str_hash(content,hashlib.sha384,encoding)
def str_sha1(content: str,encoding: str = 'UTF-8'):
    return str_hash(content,hashlib.sha1,encoding)
def str_sha224(content: str,encoding: str = 'UTF-8'):
    return str_hash(content,hashlib.sha224,encoding)
###############################################################################
#%% FTP传输
def FTP_Link(host='127.0.0.1',port=21, username='', password=''):
    '''
    建立连接
    ftp.quit()#退出
    '''
    from ftplib import FTP
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login(username, password)
    return ftp
def FTP_DWload(ftp, remotepath, localpath):
    '''
    从ftp服务器下载文件
    remotepath:远程路径
    localpath：本地路径
    '''
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()
def FTP_UPload(ftp, remotepath, localpath):
    '''
    从本地上传文件到ftp
    remotepath:远程路径
    localpath：本地路径
    '''
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()
def FTP_MkDir(ftp,path):
    return ftp.mkd(path)
def FTP_PathList(ftp,path="./"):
    return ftp.nlst(path)#文件夹列表
def FTP_FileList(ftp,path="./"):
    return ftp.dir(path)#文件列表
#%% 解压缩
def un_zip(file_name,newpath=""):
    import zipfile   
    if newpath=="" :newpath =f"{file_name.replace('.zip','').replace('.ZIP','')}_files/" 
    Mkdir(newpath)
    file = zipfile.ZipFile(file_name, 'r')
    file.extractall(newpath,file.namelist())
    file.close()
def un_gz(file_name,pathS,pathE):
    """解压GZ文件"""
    import gzip
    Mkdir(pathE)
    log.Info(f"\n先解压gz文件:\n{file_name}")
    Gzfile = gzip.GzipFile(file_name)#获取gz文件
    log.Info(f"\n写入并保存文件:\n{file_name}")
    Name = file_name.replace(".gz", "").replace(pathS,pathE)
    open(Name, "wb+").write(Gzfile.read())
    Gzfile.close()
    return  Name
###============================================================================
def un_tar(file_name,newpath=""):
    '''解压Tar'''
    import tarfile
    if newpath=="" :newpath=f"{file_name.replace('.tar','').replace('.tar','')}_files/" 
    Mkdir(newpath)
    Filetar = tarfile.open(file_name)
    names = Filetar.getnames()
    for name in names:Filetar.extract(name, newpath)
    Filetar.close()
    return newpath
###============================================================================
#%% 压缩文件
def In_tar(TarName,fileptahs):
    '''压缩文件tar.gz'''
    import tarfile
    with tarfile.open(f"{TarName}.tar.gz", "w:gz") as tar:
        for file in fileptahs:tar.add(file) 

###============================================================================
def In_zip(ZipName,fileptahs):
    '''压缩文件zip'''
    import zipfile      
    with zipfile.ZipFile(f"{ZipName}.zip", "w") as zf:
        for file in fileptahs:zf.write(file)
###============================================================================

#%% Toml配置文件操作
def SaveToml(tomlfile,filename="filename",path="./",mode="w+",encoding="utf-8"):
    '''
    a:附加写,不可读。
    a+:附加读写。追加写。
    r:只读,最常用。不创建,不存在会报错。（读二进制文件可能会读取不全）
    rb:只读。二进制文件按二进制位进行读取。不创建,不存在会报错。
    rt:只读。文本文件用二进制读取。不创建,不存在会报错。
    r+:可读写。覆盖写。不创建,不存在会报错。
    w:只写。存在则覆盖。不存在则创建。
    w+:可读写。存在则覆盖。不存在则创建。
    '''
    try:
        Mkdir(path)
        import toml
        filename=f"{path}{filename}.toml"
        with open(filename, mode,encoding=encoding) as file:
            toml.dump(tomlfile,file)
            file.close()
        log.Info(f"\n|文件: {filename} ||保存成功||")
    except Exception as exception:log.Error(str(exception))
def ReadToml(filename,path):
    try:
        import toml
        return toml.load(f"{path}{filename}.toml")
    except Exception as exception:
        log.Error(str(exception))
        return {}
#==============================================================================
#%% 文件夹目录树
from pathlib import Path
from pathlib import WindowsPath
from typing  import Optional,List
#==============================================================================
class DirectionTree():
    def __init__(self,
                 direction_name: str = 'WorkingDirection',
                 direction_path: str = '.',
                 ignore_list: Optional[List[str]] = ['\.git', '__pycache__', 'test.+', 'venv', '.+\.whl', '\.idea',
                                                     '.+\.jpg', '.+\.png', 'image', 'css', 'admin', 'tool.py',
                                                     'db.sqlite3']):
        self.owner: WindowsPath = Path(direction_path)
        self.tree: str = direction_name + '/\n'
        self.ignore_list = ignore_list
        if ignore_list is None:
            self.ignore_list = []
        self.direction_ergodic(path_object=self.owner, n=0)
    def tree_add(self, path_object: WindowsPath, n=0, last=False):
        if n > 0:
            if last:
                self.tree += '│' + ('    │' * (n - 1)) + '    └────' + path_object.name
            else:
                self.tree += '│' + ('    │' * (n - 1)) + '    ├────' + path_object.name
        else:
            if last:
                self.tree += '└' + ('──' * 2) + path_object.name
            else:
                self.tree += '├' + ('──' * 2) + path_object.name
        if path_object.is_file():
            self.tree += '\n'
            return False
        elif path_object.is_dir():
            self.tree += '/\n'
            return True
    def filter_file(self, file):
        for item in self.ignore_list:
            if re.fullmatch(item, file.name):
                return False
        return True
    def direction_ergodic(self, path_object: WindowsPath, n=0):
        dir_file: list = list(path_object.iterdir())
        dir_file.sort(key=lambda x: x.name.lower())
        dir_file = [f for f in filter(self.filter_file, dir_file)]
        for i, item in enumerate(dir_file):
            if i + 1 == len(dir_file):
                if self.tree_add(item, n, last=True):
                    self.direction_ergodic(item, n + 1)
            else:
                if self.tree_add(item, n, last=False):
                    self.direction_ergodic(item, n + 1)
#==============================================================================
def PathTree(path, Write=False, filename='Pathtree', savepath='./', arge="a"):  # 文件目录树
    PathTree = DirectionTree(direction_path=path).tree
    log.Info(PathTree)
    if Write: WriteFile(PathTree, filename, savepath, arge)

# %% 终结
if __name__ == '__main__':
    EndWithPath('../', [".py"])
    SreTarDIR()
