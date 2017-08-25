# rtp_h264
python rtph264.py
This file can simply dump the rtp h264 packet to file from gstreamer.
It can't handle the out of order rtp packets.

gstream command example:

gst-launch-1.0 rtspsrc location=rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov ! rtph264depay ! avdec_h264 ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=1236

gst-launch-1.0 rtspsrc location=rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov ! rtph264depay ! rtph264pay ! udpsink host=127.0.0.1 port=1236

