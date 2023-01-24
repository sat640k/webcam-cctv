# MIT No Attribution
#
# Copyright 2023 sat640k
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import datetime
import os
import subprocess
import time

import boto3
import cv2
import dlib

from dotenv import load_dotenv
load_dotenv()

KVS_STREAM_NAME = os.environ["KVS_STREAM_NAME"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

KVS_PRODUCER_BUILD_PATH = os.environ["KVS_PRODUCER_BUILD_PATH"]
APP_NAME = "kvs_gstreamer_sample"
RECORD_SEC = 30
EXPIRATION_MIN = 360
EXPIRATION_SEC = 60 * EXPIRATION_MIN


kvs = boto3.client("kinesisvideo")
sns = boto3.client("sns")

detector = dlib.get_frontal_face_detector()


def detect_face():
    """ Wait until faces detected using dlib """
    camera = cv2.VideoCapture(0)
    while True:
        _, frame = camera.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results, _, _ = detector.run(frame_rgb, 0)
        if results:
            break
    camera.release()
    return


def detect_motion():
    """ Wait until motion detected using dlib """
    """ 動体を検出するまで待つ """
    th = 10
    gray1 = None
    gray2 = None
    gray3 = None
    camera = cv2.VideoCapture(0)
    while True:
        _, frame = camera.read()
        gray3 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if gray2 is None:
            print("init gray2")
            #gray2 = gray3.copy().astype("float")
            gray2 = gray3
            continue
        if gray1 is None:
            print("init gray1")
            #gray1 = gray2.copy().astype("float")
            gray1 = gray2
            continue

        # フレームの絶対差分
        diff1 = cv2.absdiff(gray1, gray2)
        diff2 = cv2.absdiff(gray2, gray3)

        # 2つの差分画像の論理積
        diff = cv2.bitwise_and(diff1, diff2)

        # 二値化処理
        diff[diff < th] = 0
        diff[diff >= th] = 255
    
        # メディアンフィルタ処理（ゴマ塩ノイズ除去）
        mask = cv2.medianBlur(diff, 5)

        # 差分のあるピクセル数の割合が一定値以上だったら動体検出と判断
        moment = cv2.countNonZero(mask)
        if moment > 7000:
            print(moment)
            break

        # 次の周回にむけてフレーム画像をローテーション
        gray1 = gray2
        gray2 = gray3

    camera.release()
    return


def upload_video():
    """ Upload video using Amazon Kinesis Video Streams Producer SDK C++ """
    """ 撮影動画をアップロード """
    start = time.time()
    kvs_app = f"{KVS_PRODUCER_BUILD_PATH}/{APP_NAME}"
    try:
        subprocess.run(
            [kvs_app, KVS_STREAM_NAME],
            cwd=KVS_PRODUCER_BUILD_PATH,
            timeout=RECORD_SEC
        )
    except subprocess.TimeoutExpired:
        end = time.time()
        print("record finished")
        return start, end
    print("record interrupted")
    return None, None


def get_session_url(start, end):
    """ Get HLS streaming session URL """
    """ 撮影動画のURLを取得 """
    endpoint = kvs.get_data_endpoint(
        APIName="GET_HLS_STREAMING_SESSION_URL",
        StreamName=KVS_STREAM_NAME
    )['DataEndpoint']

    kvam = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
    url = kvam.get_hls_streaming_session_url(
        StreamName=KVS_STREAM_NAME,
        PlaybackMode="ON_DEMAND",
        ContainerFormat="MPEG_TS",
        DisplayFragmentTimestamp="ALWAYS",
        Expires=EXPIRATION_SEC,
        HLSFragmentSelector={
            "FragmentSelectorType": "PRODUCER_TIMESTAMP",
            "TimestampRange": {
                "StartTimestamp": start,
                "EndTimestamp": end,
            }
        },
    )['HLSStreamingSessionURL']
    print(f"HLS session URL: {url}")
    return url


def notify_url(url, timestamp):
    """ Notify HLS streaming session URL via Amazon SNS """
    """ 撮影を通知 """
    date = datetime.datetime.fromtimestamp(timestamp)
    subject = "通知: 撮影対象を検出しました"
    message = f"""セキュリティカメラで撮影対象を検出しました。

ストリーム名: {KVS_STREAM_NAME}
日時: {date.strftime('%Y/%m/%d %H:%M:%S')}
再生用URL: {url} ({EXPIRATION_MIN}分のみ有効です)
"""
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject=subject
    )


def main():
    print("start surveillance application")
    while True:
        # 顔を検出するまで待つ
        #detect_face()
        #print("face detected: start recording")
        # 動体を検出するまで待つ
        detect_motion()
        print("motion detected: start recording")
        # 動画を撮影する
        start, end = upload_video()
        if start and end:
            # 動画撮影に成功したら、再生URLを取得してメール通知
            url = get_session_url(start, end)
            notify_url(url, start)


if __name__ == '__main__':
    main()

