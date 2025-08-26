<!--
 * @Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
 * @Date: 2025-08-23 09:50:03
 * @LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
 * @LastEditTime: 2025-08-26 17:22:26
 * @FilePath: /mss_diting/README.md
 * @Description: 
 * 
 * Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
-->
# mss_diting
妙算服务 谛听 使用券商和其他第三方提供的接口，获取实时行情数据，按照股价、交易量的触发条件，向指定接口汇报。

目前使用的接口：
- Futu OpenAPI

规则示例：
(close > 320) AND (NOT (volume < 1000000))

``` JSON
rule = {
    "logic": "AND",
    "conditions": [
        {"field": "close", "op": ">", "value": 320},
        {"logic": "NOT", "conditions": [
            {"field": "volume", "op": "<", "value": 1000000}
        ]}
    ]
}
```

```Python
rule_json="{\"logic\": \"AND\", \"conditions\": [{\"field\": \"close\", \"op\": \">\", \"value\": 320}, {\"logic\": \"NOT\", \"conditions\": [{\"field\": \"volume\", \"op\": \"<\", \"value\": 1000000}]}]}"
```

