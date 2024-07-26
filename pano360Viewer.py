# -*- encoding: utf-8 -*-
"""
@file        :pano360Viewer.py
@description :实现支持本地全景图/本地全景视频上传查看播放
@date        :2024/07/20 16:43:46
@author      :cuixingxing
@email       :cuixingxing150@gmail.com
@version     :1.0
"""


import streamlit as st
import streamlit.components.v1 as components
import tempfile
import base64
import io
from PIL import Image
import os
import cv2

# 页面布局配置
st.set_page_config(
    page_title="360全景查看/播放器",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://ww2.mathworks.cn/",
        "Report a bug": "https://ww2.mathworks.cn/",
        "About": "# 360全景查看/播放器!",
    },
)
st.title("360全景查看/播放器:smile:")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "本Web APP支持本地全景图像，视频实时渲染/播放，上传文件即可立即得到结果展示!"
)


tab1, tab2 = st.tabs(["Image Panorama", "Video Panorama"])

with tab1:
    # 上传本地equirectangular image渲染全景图
    uploaded_file = st.file_uploader(
        "请上传本地equirectangular全景图片", type=["jpg", "png", "bmp", "jpeg"]
    )
    if uploaded_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        # 打开图片文件
        image = Image.open(uploaded_file)

        st.markdown("## 全景图原图")

        # 显示图片
        st.image(image, use_column_width=True)

        # 将图片转换为base64格式，以便在HTML中使用
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # 创建HTML内容
        html_code = f"""  
        <html>  
            <body>  
                <h1>HTML显示上传的图片</h1>  
                <img src="data:image/png;base64,{img_str}" width="400">  
            </body>  
        </html>  
        """

        # 创建HTML代码，替换panorama参数为base64字符串
        html_code = f"""  
        <!DOCTYPE HTML>  
        <html>  
        <head>  
            <meta charset="utf-8">  
            <meta name="viewport" content="width=device-width, initial-scale=1.0">  
            <title>A simple example</title>  
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.css" />  
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.js"></script>  
            <style>  
                #panorama {{  
                    width: 100%;  
                    height: 800px;  
                }}  
            </style>  
        </head>  
        <body>  
            <div id="panorama"></div>  
            <script>  
                pannellum.viewer('panorama', {{  
                    "type": "equirectangular",  
                    "panorama": "data:image/png;base64,{img_str}"  
                }});  
            </script>  
        </body>  
        </html>  
        """
        with st.container():
            # 给出MarkDown标题
            st.markdown("## 全景图渲染结果")
            st.markdown("鼠标交互操作预览(拖曳查看方向，滚轮缩放视角)")
            # 使用 streamlit.components.v1.html 显示HTML内容
            st.components.v1.html(html_code, height=800)

##########################下面是显示360全景视频 ##################################################################
with tab2:
    # 文件上传组件，允许用户上传 MP4 视频
    uploaded_file = st.file_uploader("请上传本地equirectangular全景视频", type=["mp4"])

    if uploaded_file is not None:
        st.markdown("## 全景图原始视频")
        st.video(uploaded_file)

        # 创建临时目录用以保存视频
        temp_dir = "temp_dir"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # 获取文件的文件名，并保存上传的视频文件
        video_path = os.path.join(temp_dir, uploaded_file.name)

        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 提取视频的第一帧用于poster
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 5)
        success, frame = cap.read()
        cap.release()

        # 检查是否成功获取视频帧
        if success:
            # 将图像转换为RGB格式
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 将frame转换为base64
            _, buffer = cv2.imencode(".jpg", frame)
            image_base64 = base64.b64encode(buffer).decode()
            poster_url = f"data:image/jpeg;base64,{image_base64}"
        else:
            print("can't read video.")
            poster_url = ""

        # 将视频文件读取为base64格式
        with open(video_path, "rb") as f:
            video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode()

        # # 设置poster图像的URL（可以自定义或保持默认）
        # poster_url = "https://pannellum.org/images/video/jfk-poster.jpg"

        # 创建HTML代码，替换视频源和预览图像
        html_code = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pannellum Video</title>
            <link rel="stylesheet" href="https://cdn.pannellum.org/2.4/pannellum.css"/>
            <script type="text/javascript" src="https://cdn.pannellum.org/2.4/pannellum.js"></script>
                    
                <link href="https://vjs.zencdn.net/5.4.6/video-js.css" rel="stylesheet"
            type="text/css">
            <script src="https://vjs.zencdn.net/5.4.6/video.js"></script>
            <script src="https://pannellum.org/js/videojs-pannellum-plugin.js"></script>
                
            <style>
            #panorama {{
                width: 100%;
                height: 800px;
            }}
            </style>
        </head>
        <body>
            <video id="panorama" class="video-js vjs-default-skin vjs-big-play-centered" controls preload="none" style="width:100%;height:800px;" poster="{poster_url}" crossorigin="anonymous">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4"/>			
                    <p class="vjs-no-js">
                        To view this video please enable JavaScript, and consider upgrading to a web browser that <a href="http://videojs.com/html5-video-support" target="_blank">supports HTML5 video</a>				
                    </p>
                    
                </video>
                
                <script>
                    videojs('panorama', {{
                        plugins: {{
                            pannellum: {{}}
                        }}
                    }});
                </script>
                
        </body>
        </html>
        """

        st.markdown("## 全景视频渲染结果")
        st.markdown("鼠标交互操作预览(拖曳查看方向，滚轮缩放视角)")
        # 使用 streamlit.components.v1.html 显示HTML内容
        st.components.v1.html(html_code, height=800)
