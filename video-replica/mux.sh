#!/usr/bin/env bash
# Uso: ./mux.sh narracao.(wav|mp3|mp4)   -> out/video_narrado.mp4
# O áudio é normalizado (-14 LUFS), completado com silêncio e cortado na duração do vídeo.
set -e
cd "$(dirname "$0")"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/video.mp4)
ffmpeg -v error -y -i out/video.mp4 -i "$1" \
  -filter_complex "[1:a]aresample=44100,loudnorm=I=-14:TP=-1.5,apad,atrim=0:$DUR[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 160k -shortest out/video_narrado.mp4
echo ok -> out/video_narrado.mp4
