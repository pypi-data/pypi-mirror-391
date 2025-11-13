/// 代理配置
#[derive(Clone, Default)]
pub struct ProxyConfig {
    pub url: Option<String>,
}

impl ProxyConfig {
    /// 应用到 wreq ClientBuilder
    ///
    /// 支持的代理格式（v6.0.0-rc.21+）：
    /// - http://proxy:port
    /// - socks5://proxy:port
    /// - http://user:pass@proxy:port
    /// - http://user@proxy:port (rc.21+ 支持省略密码)
    ///
    /// 注意：为避免 302 重定向时出现 407 错误，同时配置 HTTP 和 HTTPS 代理
    pub fn apply(&self, builder: wreq::ClientBuilder) -> Result<wreq::ClientBuilder, String> {
        if let Some(ref proxy_url) = self.url {
            // 将 https:// 替换为 http://（wreq 代理限制）
            let http_proxy = if proxy_url.starts_with("https://") {
                proxy_url.replacen("https://", "http://", 1)
            } else {
                proxy_url.clone()
            };

            // 分别配置 HTTP 和 HTTPS 代理，避免 302 跳转时出现 407 错误
            // 这样在协议切换（HTTP ↔ HTTPS）时代理认证信息能正确传递
            let http_proxy_obj = wreq::Proxy::http(&http_proxy)
                .map_err(|e| format!("HTTP代理配置无效: {} (代理URL: {})", e, http_proxy))?;
            let https_proxy_obj = wreq::Proxy::https(&http_proxy)
                .map_err(|e| format!("HTTPS代理配置无效: {} (代理URL: {})", e, http_proxy))?;

            Ok(builder.proxy(http_proxy_obj).proxy(https_proxy_obj))
        } else {
            // 从环境变量读取代理
            if let Ok(env_proxy) = std::env::var("PRIMP_PROXY") {
                let http_proxy = if env_proxy.starts_with("https://") {
                    env_proxy.replacen("https://", "http://", 1)
                } else {
                    env_proxy
                };

                // 同样分别配置 HTTP 和 HTTPS 代理
                let http_proxy_obj = wreq::Proxy::http(&http_proxy)
                    .map_err(|e| format!("环境变量PRIMP_PROXY HTTP代理配置无效: {} (代理URL: {})", e, http_proxy))?;
                let https_proxy_obj = wreq::Proxy::https(&http_proxy)
                    .map_err(|e| format!("环境变量PRIMP_PROXY HTTPS代理配置无效: {} (代理URL: {})", e, http_proxy))?;

                Ok(builder.proxy(http_proxy_obj).proxy(https_proxy_obj))
            } else {
                Ok(builder)
            }
        }
    }
}
