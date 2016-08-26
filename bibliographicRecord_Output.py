#-*- coding:utf-8 -*-
import os,re
from abc import ABCMeta, abstractmethod

class CRF_Train :
    Trainfile='./Trainfile'
    __metaclass__ = ABCMeta

    @abstractmethod
    def crf_learn(self,gram='B') : pass

    @classmethod
    def make_template(self,fcount,gram='') :
        if gram != 'B' and gram !='U' and gram != '' :
            print 'Wrong Input!!!'
            return
        template=[]
        count=1
        sample=['%x[-2,','%x[-1,','%x[0,','%x[1,','%x[2,',
                '%x[-2,/%x[-1,','%x[-1,/%x[0,','%x[0,/%x[1,','%x[1,/%x[2,',
                '%x[-2,/%x[-1,/%x[0,','%x[-1,/%x[0,/%x[1,', '%x[0,/%x[1,/%x[2,']
        for number in range(fcount) :
            for word in sample :
                temp=word.split('/')
                for n in range(len(temp)) :
                    temp[n]=temp[n]+str(number)+']'
                template.append((count,'/'.join(temp)))
                count=count+1

        with open('template','w') as oF :
            oF.write("#Bigram\n\n")
            for (count,line) in template :
                line=('U'+str(count)+":"+line).strip()
                if (int)(count) % len(sample) == 0 : line=line+'\n'
                oF.write(line+'\n')
            oF.write(gram)


class CRF_Test :
    Testfile='./Testfile'
    __metaclass__ = ABCMeta

    @abstractmethod
    def crf_test(self) : pass


"""

"""

class Parent_Addfeature :
    def initfilewrite(self,fileName,directory=None) :
        self.fileName=fileName
        self.directory=directory
        self.fcount=0
        Temp=[]
        if not directory :
            Temp=[line.strip() for line in open(self.fileName,'r').readlines()]
        else :
            filelist=os.listdir(directory)
            for fileName in filelist :
                Temp+=[line.strip() for line in open(directory+'/'+fileName,'r').readlines()]
                Temp+=['']

        self.filewrite(Temp)
        self.addCount()

    def mecab_feature(self,Test) :
        if Test is False :
            self.addCount()
            return
        Temp=[line.strip() for line in open(self.fileName,'r').readlines()]
        with open('Temp','w') as oF :
            for line in Temp : oF.write(line+'\n')

        os.system('mecab Temp > Temp.mecab')
        Temp=[line.strip() for line in open('Temp.mecab','r').readlines()]
        newTemp=[]
        for line in Temp :
            try :
               word=line.split('\t')[0]
               mecab=line.split('\t')[1].split(',')[0]
               newTemp.append(mecab+'\t'+word)
            except IndexError : pass

        os.system('rm Temp Temp.mecab '+self.fileName)
        self.filewrite(newTemp)
        self.addCount()


    #초록 자질
    def abstract_feature(self) :
        Temp=[line.strip() for line in open(self.fileName,'r').readlines()]
        p=re.compile('abstract|요약|초록',re.I)
        feature='O'
        newTemp=[]

        for line in Temp :
            try :
                word=line.split('\t')[self.fcount-1]
                if p.match(word) : feature='X'
                newTemp.append(feature+'\t'+line)
            except IndexError :
                feature='O'
                newTemp.append('')

        self.filewrite(newTemp)
        self.addCount()

    def filewrite(self,Temp) :
        with open(self.fileName,'w') as oF :
            for line in Temp : oF.write(line+'\n')


    def addCount(self) : self.fcount=self.fcount+1
    def getCount(self) : return self.fcount

class Addfeature(Parent_Addfeature) :
    def __init__(self,Test,fileName,directory=None) :
        Parent_Addfeature.initfilewrite(self,fileName,directory)
        Parent_Addfeature.mecab_feature(self,Test)

    #길이 자질
    def lenght_feature(self) :
        Temp=[line.strip() for line in open(self.fileName).readlines()]
        newTemp=[]
        for line in Temp :
            try:
                word=line.split()[self.fcount-1]
                length=len(word.decode('utf-8'))
                newTemp.append(str(length)+'\t'+line)
            except IndexError : newTemp.append('')
        self.filewrite(newTemp)
        self.addCount()

    #괄호 자질
    def bracket_feature(self) :
        Temp=[line.strip() for line in open(self.fileName).readlines()]
        bracket={'(':')',  '{':'}', '〔':'〕', '[':']', '「':'」','《':'》','『':'』'}
        stack=[]

        for (num,line) in enumerate(Temp) : 
            try :
                word=line.split()[self.getCount()-1]
                count=0
                if word in bracket :
                    out=bracket[word]
                    for num2 in range(num+1,len(Temp)) :
                        tWord=Temp[num2].split()[self.getCount()-1]
                        if tWord == out : break
                        else : count=count+1
                    stack.append((num,num2,count))
            except IndexError : pass
        newTemp=[]
        for line in Temp :
            if line=='' :
                newTemp.append('')
                continue
            newTemp.append('0\t'+line)
        for (num,num2,count) in stack :
            for number in range(num+1,num2) :
                line=str(count)+'\t'+'\t'.join(newTemp[number].split()[1:])
                newTemp[number]=line

        self.filewrite(newTemp)
        self.addCount()

    #글자 구분 자질
    def word_division(self) :
        Temp=[line.strip() for line in open(self.fileName).readlines()]
        mark=['SF','SE','SS','SP','SO','SW','SE','SSO','SSC','SC','SY']
        english='SL'
        chinese='SH'
        number='SN'
        newTemp=[]
        for num in range(len(Temp)) :
            try :
                word=Temp[num].split()[self.fcount-2]
                if word in mark : Temp[num]='M\t'+Temp[num]
                elif word==english : Temp[num]='E\t'+Temp[num]
                elif word==number : Temp[num]='N\t'+Temp[num]
                elif word==chinese : Temp[num]='C\t'+Temp[num]
                else : Temp[num]='K\t'+Temp[num]
            except IndexError : pass
        self.filewrite(Temp)
        self.addCount()


class Abstract_Addfeature(Parent_Addfeature) :
    def __init__(self,Test,fileName,directory=None) :
        Parent_Addfeature.initfilewrite(self,fileName,directory)
        Parent_Addfeature.mecab_feature(self,Test)
        t = Parent_Addfeature.getCount(self)

    def method(self) : pass


class Parent_file :
    modelDirectory='./Model'
    resultDirectory='./result'
    modelName=''
    resultName=''
    fcount=0
    def __init__(self,fileName,directory=None) :
        self.fileName=fileName
        self.directory=directory

    def setfileName(self,fileName) : self.fileName=fileName
    def getfileName(self) : return self.fileName
    def setdirectory(self,directory) : self.directory=directory
    def getdirectory(self) : return self.directory

    def getmodelName(self) : return self.modelName
    def setmodelName(self,modelName) : self.modelName=modelName
    def getresultName(self) : return self.resultName
    def setresultName(self,resultName) : self.resultName=resultName



class Abstract_file(Parent_file) :
    def __init__(self,fileName,directory=None) :
        Parent_file.__init__(self,fileName,directory)
        Parent_file.setmodelName(self,self.modelDirectory+'/Abstract_model')
        Parent_file.setresultName(self,self.resultDirectory+'/result')

        if isinstance(self,Abstract_Test) :
            self.feature=Abstract_Addfeature(True,fileName)
        elif isinstance(self,Abstract_Train) :
            self.feature=Abstract_Addfeature(False,fileName,directory)


    def makefile(self) :
        self.feature.abstract_feature()
        self.fcount=self.getCount()


    def getCount(self) : return self.feature.getCount()

class Abstract_Train(Abstract_file,CRF_Train) :
    def __init__(self,fileName,directory) :
        fileName=self.Trainfile+'/'+fileName
        Abstract_file.__init__(self,fileName,directory)

    def crf_learn(self,gram='') :
        fileName=self.getfileName()
        modelName=self.getmodelName()
        fcount=self.getCount()
        self.make_template(fcount,gram)
        os.system('crf_learn -f '+str(fcount)+' template '+fileName+' '+modelName)

class Abstract_Test(Abstract_file,CRF_Test) :
    def __init__(self,fileName) :
        fileName = self.Testfile+'/'+fileName
        Abstract_file.__init__(self,fileName)

    def crf_test(self) :
        result=self.getresultName()
        modelName=self.getmodelName()
        fileName=self.getfileName()
        os.system('crf_test -m '+modelName+' '+fileName+' > '+result)

class bibliographicRecord_file(Parent_file) :
    def __init__(self,fileName,directory=None) :
        Parent_file.__init__(self,fileName,directory)
        Parent_file.setmodelName(self,self.modelDirectory+'/model')      #modelfile
        Parent_file.setresultName(self,self.resultDirectory+'/result')    #resultfile
        if isinstance(self,Test) :
            self.feature=Addfeature(True,fileName)
        elif isinstance(self,Train) :
            self.feature=Addfeature(False,fileName,directory)

    #자질들을 추가한다.
    def makefile(self) :
        self.feature.lenght_feature()
        self.feature.word_division()
        self.feature.bracket_feature()
        self.feature.abstract_feature()
        self.fcount=self.getCount()

    def getCount(self) : return self.feature.getCount()

class Train(bibliographicRecord_file,CRF_Train) :
    def __init__(self,fileName,directory) :
        fileName=self.Trainfile+'/'+fileName
        bibliographicRecord_file.__init__(self,fileName,directory)

    def crf_learn(self,gram='') :
        fileName=self.getfileName()
        modelName=self.getmodelName()
        fcount=self.getCount()
        self.make_template(fcount,gram)
        os.system('crf_learn -f '+str(fcount)+' template '+fileName+' '+modelName)

    def connect_Abstract(self) :
        aTrain=Abstract_Train('Abstract_Train','../Data/abstract')
        aTrain.makefile()
        aTrain.crf_learn('B')
        origin_fileName = self.getfileName()
        fileName = aTrain.getfileName()

        Temp=[line.strip() for line in open(fileName,'r').readlines()]
        originTemp=[line.strip() for line in open(origin_fileName,'r').readlines()]
        newTemp=[]
        for num in range(len(Temp)) :
            try :
                word=Temp[num].split()[aTrain.getCount()]
                if word == 'P' : newTemp.append(originTemp[num])
            except IndexError: newTemp.append('')
        self.feature.filewrite(newTemp)


class Test(bibliographicRecord_file,CRF_Test) :
    def __init__(self,fileName) :
        self.copyfile=fileName+'.copy'
        fileName=self.Testfile+'/'+fileName
        os.system('cp '+fileName+' '+self.Testfile+'/'+self.copyfile)
        os.system('cp '+fileName+' '+fileName+'.formet')

        fileName=fileName+'.formet' #파일의 이름을 ~~.formet으로 한다.
        self.initmakeformetfile(fileName)
        bibliographicRecord_file.__init__(self,fileName)
        self.Test_on=False

    def initmakeformetfile(self,fileName) :
        Temp=[]
        with open(fileName,'r') as oF :
           while True :
               line=oF.readline()
               if not line : break
               if line == '\n' : Temp.append('...//')
               for word in line.split() : Temp.append(word.strip())

        with open(fileName,'w') as oF :
            for line in Temp : oF.write(line.strip()+'\n')

    def __del__(self) :
        os.system('rm '+self.Testfile+'/'+self.copyfile)

    def crf_test(self) :
        result=self.getresultName()
        modelName=self.getmodelName()
        fileName=self.getfileName()
        os.system('crf_test -m '+modelName+' '+fileName+' > '+result)
        self.Test_on=True



    def output(self) :
        if self.Test_on :  bibliographicRecord.result(self.getresultName(),self.getCount())
        else :
            print "not executes crf_test(self)"
            return

    def connect_Abstract(self) :
        aTest=Abstract_Test(self.copyfile)
        if not os.path.exists(aTest.getmodelName()) : 
            print "not exist "+aTest.getmodelName()+" you must Train(excutes crf_learn())"
        aTest.makefile()
        aTest.crf_test()
        result=aTest.getresultName()

        Temp=[line.strip() for line in open(self.getfileName(),'r').readlines()]
        rTemp=[line.strip() for line in open(result,'r').readlines()]
        newTemp=[]
        for num in range(len(rTemp)) :
            try :
                word=rTemp[num].split()[aTest.getCount()]
                if word == 'P' : newTemp.append(Temp[num])
            except IndexError : newTemp.append('')
        self.feature.filewrite(newTemp)

class bibliographicRecord :
    @staticmethod
    def result(fileName,fcount) :
        recode={
                'A':[], 'J':[], 'N':[], 'P':[], 'T':[], 'V':[], 'Y':[], 'O':[]
                }
        Temp=[line.strip() for line in open(fileName).readlines()]
        for line in Temp :
            if line=='' : continue
            word,feature=line.split('\t')[fcount-1],line.split('\t')[fcount]
            TempList=recode[feature]
            TempList.append(word)
            recode[feature]=TempList
        for key in recode.keys() :
            if key == 'O' : continue
            print key + '\t' + ' '.join(recode[key])


os.system('cp ../Data/dataset/dataset2 ./Testfile')
if __name__ == '__main__' :
    Train=Train('Train','../Data/dataset')
    Train.makefile()
    Train.crf_learn()
