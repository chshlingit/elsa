
#---------------------------------------Input video file upload-------------------------------------------------
#   【O】Input video file
#  Enter the name of the video file to be analyzed.
#  If the width is not 1280 or if the frame rate is not 30 fps, re-encoding is performed.
# Enter the parameters for tracing the image and execute the cell.

#-----------------------------------------Parameter setting------------------------------------------------------
#  【O】Maximum number of people in the video
# Please enter the number of people you want to get from the video.
# Please process the video data as much as possible for this number of people.
number_people_max = 1  #@param {type: "number"}

# ---

#  【O】Frame number to start analysis
# Enter the frame number to start analysis. (0 beginning)
# If the human body can not be traced accurately, for example, if the logo is displayed first, specify the first frame in which all the members appear in the image.
frame_first = 0  #@param {type: "number"}

# ---

#  【M】Frame number to finish analysis
# Please enter the frame number to finish the analysis. (0 beginning)
# When you adjust the reverse or order in "FCRN-DepthPrediction-vmd", you can finish the process and see the result without outputting to the end.
# If the default value is "-1", analysis is performed to the end.
end_frame_no = -1  #@param {type: "number"}

# ---

#  【M】Reverse specification list
# Specify the frame number (0 starting) that is inverted by Openpose by mistake, the person INDEX order, and the contents of the inversion.
# In the order that Openpose recognizes at 0F, INDEX is assigned as 0, 1, ....
# Format: [{frame number}: Person who wants to specify reverse INDEX, {reverse content}]
# {reverse content}: R: Whole body inversion, U: Upper body inversion, L: Lower body inversion, N: No inversion
# ex）[10:1,R]　…　The whole person flips the first person in the 10th frame.
# Since the contents are output in the above format in message.log when inverted output, please refer to that.
# As in [10:1,R][30:0,U], multiple items can be specified in parentheses.
reverse_specific = ""  #@param {type: "string"}

# ---

#  【M】Ordered list
# In the multi-person trace, please specify the person INDEX order after crossing.
# In the case of a one-person trace, it is OK to leave it blank.
# In the order that Openpose recognizes at 0F, INDEX is assigned as 0, 1, ....
# Format: [{frame number}: index of first estimated person, index of first estimated person, ...]
# 例）[10:1,0]　…　The order of the 10th frame is rearranged in the order of the first person from the left and the zeroth person.
# The order in which messages are output in message.log is left in the above format, so please refer to it.
# As in [10:1,0][30:0,1], multiple items can be specified in parentheses.
# Also, in output_XXX.avi, colors are assigned to people in the estimated order. The right half of the body is red and the left half is the following color.
# 0: green, 1: blue, 2: white, 3: yellow, 4: peach, 5: light blue, 6: dark green, 7: dark blue, 8: gray, 9: dark yellow, 10: dark peach, 11: dark light blue
order_specific = ""  #@param {type: "string"}

# ---

#  【V】Bone structure CSV file
# Select or enter the path of the bone structure CSV file of the trace target model.
# You can select "Animasa-Miku" and "Animasa-Miku semi-standard", or you can input a bone structure CSV file of any model.
# If you want to input any model bone structure CSV file, please upload the csv file to the "autotrace" folder of Google Drive.
# And please enter like「/gdrive/My Drive/autotrace/[csv file name]」
born_model_csv = "born/animasa_miku_born.csv" #@param ["born/animasa_miku_born.csv", "born/animasa_miku_semi_standard_born.csv"] {allow-input: true}


# ---

#  【V】Whether to output with IK
# Output the foot of trace data as IK, or select yes or no.
# If you enter no, output with FK
ik_flag = "yes"  #@param ['yes', 'no']
is_ik = 1 if ik_flag == "yes" else 0

# ---

#  【V】Heel position correction
# Please input the Y axis correction value of the heel with a numerical value (decimal possible).
# Entering a negative value approaches the ground, entering a positive value moves away from the ground.
# Although it corrects automatically to some extent automatically, if you can not correct it, please set it.
heel_position = 0.0  #@param {type: "number"}

# ---

#  【V】Center-Z moving magnification
# Please enter the magnification multiplied by the center Z movement with a numerical value (decimal possible).
# The smaller the value, the smaller the width of the center Z movement.
# When 0 is input, center Z axis movement is not performed.
center_z_scale = 1.5  #@param {type: "number"}

# ---

#  【V】Center-Z Smoothing frequency
# Specify the degree of motion smoothing center-z
# Please enter only an integer of 1 or more.
# The larger the frequency, the smoother it is. (The behavior will be smaller instead)
depth_smooth_times = 4  #@param {type: "number"}

# ---

#  【V】Smoothing frequency
# Specify the degree of motion smoothing
# Please enter only an integer of 1 or more.
# The larger the frequency, the smoother it is. (The behavior will be smaller instead)
smooth_times = 1  #@param {type: "number"}

# ---

#  【V】Movement key thinning amount
# Specify the amount of movement to be used for decimation of movement key (IK, center) with numerical value (decimal possible)
# When there is a movement within the specified range, it is thinned out.
# When moving thinning amount is set to 0, thinning is not performed.
threshold_pos = 0.5  #@param {type: "number"}

# ---

#  【V】Rotating Key Culling Angle
# Specify the angle (decimal possible from 0 to 180 degrees) to be used for decimating rotation keys
# It will be thinned out if there is a rotation within the specified angle.
threshold_rot = 3  #@param {type: "number"}
#-----------------------Auto Trace execution------------------------------------------------------------
#  Please execute this cell after completing all the forms.
#  Processing is performed in the following order.

#  1. Openpose（Video→2D）
#  2. mannequinchallenge-vmd（Depth estimation）
#  3. 3d-pose-baseline-vmd（2D→3D）
#  4. VMD-3d-pose-baseline-multi（3D→VMD）

#  Depending on the number of traces, it takes about 50 to 60 minutes in 6000 frames.
#  When Openpose starts, it looks like it has stopped moving for a while with its elongated square.
#  If the playback button is spinning around, processing is taking place behind the scenes, so please wait without doing anything.
#  If the vmd file has not been generated, the contents of pos.txt are empty, there is only error.txt, etc., first check the contents of error.txt, and check and execute the "If an error occurs" section please do it.
#----------------------------------------                      --------------------------------------------------------
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('filepath', default='input.mp4',
                    help='filepath')

args = parser.parse_args()


input_video_name = args.filepath  # @param {type: "string"}


import os
import cv2
import datetime
import time
import shutil
import glob


# 起始目錄
base_path2 = "/home/user/Documents/elsa/ELSA/media"
output2="/home/user/Documents/elsa/ELSA/media/vmd"
base_path="/home/user/Documents/autotrace"

os.system("--------------------")
os.system("ls -l "+base_path)
os.system("--------------------")

# Input video file upload


# 起始目錄影片
input_video = base_path2 + "/" + input_video_name

print("Filename: ", os.path.basename(input_video))
print("Filesize: ", os.path.getsize(input_video))

video = cv2.VideoCapture(input_video)
# 寬
W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
# 高
H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
# 總偵數
count = video.get(cv2.CAP_PROP_FRAME_COUNT)
# fps
fps = video.get(cv2.CAP_PROP_FPS)

print("width: {0}, height: {1}, frames: {2}, fps: {3}".format(W, H, count, fps))

width = 1280
height = 720

#if W != 1280 or (fps != 30 and fps != 60):
print("Re-encode because size or fps is out of processing: " + input_video)

    # 尺寸
scale = width / W

    # 高
height = int(H * scale)

    # 輸出路徑
out_name = 'recode_{0}.mp4'.format("{0:%Y%m%d_%H%M%S}".format(datetime.datetime.now()))
out_path = '{0}/{1}'.format(base_path, out_name)
   
try:
        fourcc = cv2.VideoWriter_fourcc(*"MP4V")
        out = cv2.VideoWriter(out_path, fourcc, 30.0, (width, height), True)
        # 輸入檔案
        cap = cv2.VideoCapture(input_video)

        while (cap.isOpened()):
            # 獲取檔案並載入
            flag, frame = cap.read()  # Capture frame-by-frame

            # 影片結束時結束
            if flag == False:
                break

            # 縮小
            output_frame = cv2.resize(frame, (width, height))

            # 輸出
            out.write(output_frame)

        # 完成後開啟
        out.release()
except Exception as e:
        print("Re-encoding failed", e)

cap.release()
cv2.destroyAllWindows()

print('Regenerate MP4 file for MMD input', out_path)
input_video_name = out_name

    # 視頻影片重置
input_video = base_path + "/" + input_video_name

video = cv2.VideoCapture(input_video)
    # 寬
W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    # 高
H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # 總偵數
count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    # fps
fps = video.get(cv2.CAP_PROP_FPS)

print("[Re-check] width: {0}, height: {1}, frames: {2}, fps: {3}".format(W, H, count, fps))


os.system("The input video is" + input_video_name)
os.system("----------------------------")
os.system("If there is no problem, proceed to the next.")



# Parameter setting

if not os.path.exists("/home/user/Documents/autotrace/VMD-3d-pose-baseline-multi/{0}".format(born_model_csv)):
    # 如果現有骨架結構CSV不存在，請參考
    born_model_csv = "/home/user/Documents/autotrace/{0}".format(born_model_csv)
    if not os.path.exists(born_model_csv):
        os.system("■■■■■■■■■■■■■■■■")
        os.system("■ WARNING")
        os.system("■ Bone structure CSV not found. Check the file name.")
        os.system("■ "+ born_model_csv)
        os.system("■■■■■■■■■■■■■■■■")


os.system("【O】Maximum number of people in the video:" + str(number_people_max))
os.system("【O】Frame number to start analysis:" + str(frame_first))
os.system("【F】Frame number to finish analysis:" + str(end_frame_no))
os.system("【F】Reverse specification list: " + str(reverse_specific))
os.system("【F】Ordered list: "+ str(order_specific))
os.system("【V】Bone structure CSV file: "+str(born_model_csv))
os.system("【V】Whether to output with IK: "+str(ik_flag))
os.system("【V】Heel position correction: " + str(heel_position))
os.system("【V】Center Z moving magnification: " + str(center_z_scale))
os.system("【V】Smoothing frequency: " + str(smooth_times))
os.system("【V】Movement key thinning amount: " + str(threshold_pos))
os.system("【V】Rotating Key Culling Angle: " + str(threshold_rot))

os.system("-------------------------------------------------")
os.system("If the above is correct, please proceed to the next.")


# Auto Trace execution

start_time = time.time()

#刪除輸出資料夾
if os.path.exists("/home/user/Documents/autotrace/openpose/output"):
    os.system("rm -r /home/user/Documents/autotrace/openpose/output")
    print("output資料夾刪除")
# 當前時間
now_str = "{0:%Y%m%d_%H%M%S}".format(datetime.datetime.now())


# 起始目錄
drive_base_dir = "/home/user/Documents/autotrace"
#json檔輸出目錄
output_json = "/home/user/Documents/autotrace/openpose/output/json"
#轉換影片輸出路徑
output_openpose_avi = "openpose/output/openpose.avi"
#建立檔案輸出資料夾
os.system("mkdir  -p  "+ output_json)


# 建立檔案輸出資料夾
drive_dir_path = drive_base_dir + "/" + now_str
os.mkdir (drive_dir_path)

print(" - -----------------------------------------")
print("    Openpose")
print(" - -----------------------------------------")

# Openpose実行
os.system ("cd /home/user/Documents/autotrace/openpose && ./build/examples/openpose/openpose.bin --video " + out_path + "  --display 0 --model_pose COCO --write_json /home/user/Documents/autotrace/openpose/output/json --write_video /home/user/Documents/autotrace/openpose/output/openpose.avi  --frame_first 0 --number_people_max " +  str(number_people_max) )


print(" - -----------------------------------------")
print(" mannequinchallenge - vmd")
print(" - -----------------------------------------")
os.system(" cd /home/user/Documents/autotrace/mannequinchallenge-vmd && python3 predict_video.py    --video_path " + out_path + "  --json_path /home/user/Documents/autotrace/openpose/output/json --interval 20  --verbose 1 --now "+  now_str + "  --avi_output ""\""+"yes"+"\"""  --number_people_max " + str(number_people_max) + " --end_frame_no -1  --input single_view --batchSize 1 ")


# 復制結果
depth_dir_path = output_json + "_" + now_str + "_depth"

if os.path.exists(depth_dir_path + "/error.txt"):

    # 錯誤訊息
    os.system("cp "+ depth_dir_path+"/error.txt" + " "+drive_dir_path)
    print("■■■■■■■■■■■■■■■■■■■■■■■■")
    print("■■Processing was interrupted due to an error.")
    print("■■")
    print("■■■■■■■■■■■■■■■■■■■■■■■■")
    print(drive_dir_path +" - Check the contents of error.txt.")


else:
    os.system("cp -r  " + depth_dir_path + " " + drive_dir_path)


    for i in range(1, number_people_max + 1):

        print("- -----------------------------------------")
        print("3d-pose-baseline-vmd ["+ str(i) +"]")
        print("- -----------------------------------------")

        target_name = "_" + now_str + "_idx0" + str(i)
        target_dir = output_json + target_name
        os.system("	cd /home/user/Documents/autotrace/3d-pose-baseline-vmd && python3 src/openpose_3dpose_sandbox_vmd.py --camera_frame --residual --batch_norm --dropout 0.5 --max_norm --evaluateActionWise --use_sh --epochs 200 --load 4874200 --gif_fps 30 --verbose 1 --openpose " + target_dir + " --person_idx 1   ")


        print("- -----------------------------------------")
        print ("VMD-3d-pose-baseline-multi ["+ str(i)+"]")
        print("- -----------------------------------------")

        os.system("cd /home/user/Documents/autotrace/VMD-3d-pose-baseline-multi && python3 main.py -v 2 -t "+  target_dir +"  -b born/animasa_miku_born.csv  -c 30 -z  1.5  -s  1 -p 0.5 -r 3 -k  1  -e 0.0 -d 4 ")

        # INDEX結果複制
        idx_dir_path = drive_dir_path + "/idx0" + str(i)
        os.system("mkdir -p "+ idx_dir_path)
        # 日語python複制
        for f in glob.glob(target_dir + "/*.vmd"):
            shutil.copy(f, idx_dir_path)
        shutil.copy(target_dir + "/pos.txt", idx_dir_path)
        shutil.copy(target_dir + "/start_frame.txt", idx_dir_path)
       	os.system("cp -r  "+target_dir+" "+output2)
        os.system("cp /home/user/Documents/autotrace/openpose/output/openpose.avi "+output2+"/json_" + now_str + "_idx0" + str(i)+"/openpose.avi")	
       	jaon_path = "/json_" + now_str + "_idx0" + str(i) +"/"
       	path = output2 + jaon_path +"*.vmd"
       	mmd_output = "/home/user/Documents/elsa/mmd-viewer-js/vmd/motion.vmd"
       	os.system("cp %s %s" %(path, mmd_output))
print(target_dir)
print(idx_dir_path)


