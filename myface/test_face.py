#导包
from flask import Flask,render_template,request
#如果前端json,需要一个json模块
import json
#导入时间模块
import time
#导入数据库模块
import pymysql
#导入pillow模块当中的图片
from PIL import Image
#导入base64的编码包
import base64
#导入人脸识别的包
#两个函数：第一个读取图片文件 load_image_file
#第二个函数：确定脸部位置 face_locations
from face_recognition import load_image_file,face_locations
app=Flask(__name__,template_folder="myfolder",static_folder="myimg")
@app.route("/")
def index001():
	return render_template("index001.html")
@app.route("/index")
def hello():
	return render_template("index.html")
#用户通过返回的页面，点击“拍照”后用户就要把数据上传到flask中
#点击“拍照”后要有第二个地址接收数据。
#在请求地址时，把方式中GET和POST都允许
@app.route("/address",methods=["GET","POST"])
def address():
	#接收前端的数据，固定的
	datas=request.form.get("img")
	#对前端的base64编码数据进行解码
	b64img=base64.b64decode(datas)
	#输出图片看一下效果，图片是字节写入，所以是wb
	with open("a.jpg","wb") as f:
		f.write(b64img)
	#机器处理的数据是ndarray，写图片用的编码base64
	#通过存储图片，通过load_image_file把图片转成ndarray
	myimage=load_image_file("a.jpg")
	facelocations=face_locations(myimage)
	#print(facelocations)
	#print可以知道列表是否有数据，没有数据后面的代码报错
	#遍历列表中的每个元素，取出图片中辩识出的每个人脸
	for facelocation in facelocations:
		#把facelocation数据直接接收，接收到四个参数
		#x,y,w,h机器学习的记录,
		#从上面顺时针数
		# 上，右，下，左顺序，top,right,bottom,left开发,上下行，左右列
		top,right,bottom,left=facelocation
		#切片截取数据,切片数据对ndarray的图片myimg
		#print(myimage[top:bottom,left:right,:])
		cut_face=myimage[top:bottom,left:right,:]
		#
		# #cut_face中的ndarray类型如何转成base64编码
		# #把ndarray转成图片可以通过pillow，有一个方法fromarray
		# #这时的cut_face是一个ndarray,fromarray功能把ndarrray转成图片
		cut_img=Image.fromarray(cut_face)
		# #把转化的切开的脸存成一个图片，
		cut_img.save("b.jpg")
		#存成图片，就是一个图片数据,前端的图片显示的base64
		#这里需要把b.jpg做一个base64的编码
		with open("b.jpg","rb") as f:
			codes=base64.b64encode(f.read())

		#去掉b，把base64编码转成utf8的格式，b是unicode格式
		codes=codes.decode("utf8")
		#print(codes)
		#先取当前时间
		import time
		mytime = time.localtime()
		#print(mytime)
		# 把时间转化成"年月日 时:分:秒",这个start_time就是一个签到时间
		start_time=time.strftime("%Y{}%m{}%d{} %H:%M:%S", mytime).\
			format("年", "月", "日")
		# codes中存储的是base64数据
		#连接数据库：第一步connect连接数据库
		#连接数据库四要素：数据库主机，数据库端口号3306,数据库登陆用户名，密码
		#连接数据库，事先建立好数据库.
		conn=pymysql.connect(host="localhost",port=3306,user="root",
						password="123456",database="qiandao")
		#连接数据库后获取游标,cursor取的是数据库中游动的指示
		cursor=conn.cursor()
		#execute作用执行一条sql语句ode
		cursor.execute("insert into faces(id,face,qiandao,qiantui) "
					   "values(%s,%s,%s,%s)",(1,codes,start_time,None))
		#mysql是一个事务型的管理，如果只是执行语句，不提交，写不到数据库
		conn.commit()
		conn.close()
	return json.dumps({"imgcode":codes,"start_time":start_time},
					  ensure_ascii=False)

@app.route("/logout",methods=["GET","POST"])
def logout():
	#获取前端的数据
	data=request.form.get("img_data")
	#当前数据就是base64的编码
	#连接数据库
	conn=pymysql.connect(host="localhost",port=3306,user="root",password="123456",database="qiandao")
	#取游标
	cursor=conn.cursor()
	#执行查询的sql语句
	cursor.execute("select * from faces where face=%s",data)
	#查询可以通过fetchall方法获取数据库查询的所有记录
	result=cursor.fetchall()
	import time
	mytime = time.localtime()
	# print(mytime)
	# 把时间转化成"年月日 时:分:秒",这个start_time就是一个签到时间
	end_time = time.strftime("%Y{}%m{}%d{} %H:%M:%S", mytime).format("年", "月", "日")
	if len(result)>0:
		cursor.execute("update faces set qiantui=%s where face=%s",(end_time,data))
		conn.commit()
	return json.dumps({"end_time":end_time},ensure_ascii=False)

if __name__=="__main__":
	app.run()
