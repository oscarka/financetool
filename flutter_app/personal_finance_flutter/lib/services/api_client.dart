import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import '../models/asset_snapshot.dart';

part 'api_client.g.dart';

@RestApi()
abstract class ApiClient {
  factory ApiClient(Dio dio, {String baseUrl}) = _ApiClient;

  @GET('/api/snapshot/assets')
  Future<List<AssetSnapshot>> getAssetSnapshots(
    @Query('start_date') String? startDate,
    @Query('end_date') String? endDate,
    @Query('platform') String? platform,
    @Query('base_currency') String? baseCurrency,
  );

  @POST('/api/snapshot/extract')
  Future<void> triggerAssetSnapshot();
}

class ApiConfig {
  // 使用原项目的后端API地址
  static const String baseUrl = 'https://personal-finance-backend-production-3b0b.up.railway.app';
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;
}

// 创建Dio实例
Dio createDio() {
  final dio = Dio();
  
  dio.options.baseUrl = ApiConfig.baseUrl;
  dio.options.connectTimeout = const Duration(milliseconds: ApiConfig.connectTimeout);
  dio.options.receiveTimeout = const Duration(milliseconds: ApiConfig.receiveTimeout);
  
  // 添加拦截器
  dio.interceptors.add(LogInterceptor(
    requestBody: true,
    responseBody: true,
    logPrint: (obj) => print(obj),
  ));
  
  return dio;
}