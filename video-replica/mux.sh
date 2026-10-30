#!/usr/bin/env bash
# Uso: ./mux.sh narracao.wav   -> out/video_narrado.mp4
# O áudio é ajustado/atrasado para caber nos 46,8s do vídeo (sem recodificar o vídeo).
set -e
cd "$(dirname "$0")"
ffmpeg -v error -y -i out/video.mp4 -i "$1" \
  -filter_complex "[1:a]apad,atrim=0:46.8,loudnorm=I=-14:TP=-1.5[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 160k -shortest out/video_narrado.mp4
echo ok -> out/video_narrado.mp4
