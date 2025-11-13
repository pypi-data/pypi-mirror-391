# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-08-31 17:41
# @Author : 毛鹏
from mangoautomation.uidrive import DriverObject

d = DriverObject(1, )
d.set_web(web_type=2,  # type: ignore
          web_path=3,  # type: ignore
          web_max=1,
          web_headers=4,
          web_recording=5,
          web_h5=1,
          web_is_default=1,  # type: ignore
          videos_path=2,
          user_cache_path=3)
