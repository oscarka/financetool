import 'package:flutter/foundation.dart';

class DebugLogger {
  static void log(String message) {
    if (kDebugMode) {
      print(message);
    }
  }
  
  static void logError(String message) {
    if (kDebugMode) {
      print('❌ $message');
    }
  }
  
  static void logWarning(String message) {
    if (kDebugMode) {
      print('⚠️ $message');
    }
  }
  
  static void logSuccess(String message) {
    if (kDebugMode) {
      print('✅ $message');
    }
  }
  
  static void logInfo(String message) {
    if (kDebugMode) {
      print('🔍 $message');
    }
  }
}
