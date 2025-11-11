"""
pd可以直接在此写测试脚本。而无须每次都打包和安装finosdk。
注意，运行此测试的python 环境不能是finosdk的安装环境。
如果finosdk安装在虚拟环境中，建议uninstall finosdk，再运行此测试脚本。
"""
import finosdk as fino

BASE_URL = "http://127.0.0.1:20003/data_api"   # ← 改成你的
API_KEY  = "FV_DEV_4c5cbe33d7f14929978f4e83e0d4b2c5b59b6b8d79e74c1e9e5f09dd13a6b2b0"                        # ← 改成你的测试 key

fino.init(base_url=BASE_URL, api_key=API_KEY)

df = fino.get_fac_position(
    start_date="20250102",               
    end_date="20250130",                 
    code_list=["JD"],
    factor=["Pr_netmom_k90"],
    section=["农产品"]
)
print(df)


# df = fino.get_fac_trend(
#     start_date='20250102',               
#     end_date='20250205',                 
#     code_list=["A"],
#     factor=[],
#     section=['农产品']
# )
# print(df)


# df_test_data = fino.get_csft_test_data(
#     start_date="20250829",
#     end_date="20250912",
#     factor=[],
# )
# print(df_test_data)

# df_test_perf =  fino.get_csft_test_perf(
#     start_date="20250829",
#     end_date="20250912",
#     factor=[],
# )
# print(df_test_perf.head())


# df_test_dcp =  fino.get_csft_test_dcp(
#     start_date="20250503",
#     end_date="20250510",
#     factor=[],
# )
# print(df_test_dcp.head())

# df_bkt_data = fino.get_csft_bkt_data(
#     start_date="20250829",
#     end_date="20250912",
#     factor=[],
# )
# print(df_bkt_data.head())

# df_bkt_perf =  fino.get_csft_bkt_perf(
#     start_date="20250829",
#     end_date="20250912",
#     factor=[],
# )
# print(df_bkt_perf.head())


# df_bkt_dcp =  fino.get_csft_bkt_dcp(
#     start_date="20250901",
#     end_date="20250912",
#     factor=[],
# )
# print(df_bkt_dcp.head(30))


