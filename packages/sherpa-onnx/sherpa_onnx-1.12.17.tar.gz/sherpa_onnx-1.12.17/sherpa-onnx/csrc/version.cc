// sherpa-onnx/csrc/version.h
//
// Copyright      2025  Xiaomi Corporation

#include "sherpa-onnx/csrc/version.h"

namespace sherpa_onnx {

const char *GetGitDate() {
  static const char *date = "Thu Nov 13 22:35:30 2025";
  return date;
}

const char *GetGitSha1() {
  static const char *sha1 = "b1251d0d";
  return sha1;
}

const char *GetVersionStr() {
  static const char *version = "1.12.17";
  return version;
}

}  // namespace sherpa_onnx
