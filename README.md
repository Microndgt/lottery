抽奖活动设计
======

抽奖活动的demo使用了flask实现简单的服务器, sqlite3实现了数据库,完成了创建用户,获取用户所有抽奖信息,创建新的抽奖,用户抽奖,开奖以及用户的击败比例。

数据库设计
-----

数据库使用了sqlite3。因为一个用户可能对应多个奖项的多个奖号,一个奖项也可能对应了多个用户。但是相对于庞大的用户来讲,抽奖的种类是有限的,所以数据表一共分为三类,分别是用户表,用户抽奖记录表和每一种奖项的奖号记录表,其中奖号记录表对于每一种奖项就会有一张表,每张表中存储每一个奖号的详细信息。

- 用户表

用户的信息记录,包含以下字段:`ID`, `USERNAME`,分表表示用户ID, 用户名, 用户名唯一,将`USERNAME`作为索引

- 用户抽奖记录表

所有用户每次抽奖的记录,包含以下字段:`ID`, `USER_ID`, `LOTTERY_NAME`, `LOTTERY_ID`,分别表示记录ID, 用户ID, 抽奖名称, 抽奖号, 将`LOTTERY_NAME`和`LOTTERY_ID`作为索引

- 奖项奖号表

某奖项所有发出的奖号记录,每一种奖项为独立的一张表,表的名称和用户抽奖记录表中的`LOTTERY_NAME`相对应,包含以下字段:`ID`, `GEN_TIME`, `WIN`,分别表示抽奖号,抽奖时间,是否中奖,其中`WIN`作为索引

主要有以下两种查询

- 通过USER查询LOTTERY

通过`USER_ID`在`USERLOTTERY`表中查询到`LOTTERY_NAME`和`LOTTERY_ID`,通过这两列内容就可以在相应的奖号记录表中查询到所需的数据

- 通过LOTTERY_NAME和LOTTERY_ID查询USER(即开奖)

通过`LOTTERY_NAME`和`LOTTERY_ID`在`USERLOTTERY`表中查询到`USER_ID`即可。

API设计
-----

使用Flask实现一个简单的web服务器,用来模拟这个抽奖过程,实现了以下API

/user/ (POST)
---

- 功能: 创建用户

- 请求方法: POST

- 参数说明: (JSON)

|    参数    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   username    | string |  用户名 |

- 返回

|    名称    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   msg    | string | 返回信息 |
|   user_id    | int | 用户ID |
|   username    | string | 用户名 |

- 实例

```
{
  "msg": "success",
  "user_id": 4,
  "username": "kevin"
}
```

/user/ (GET)
---

- 功能: 获取用户抽奖信息

- 请求方式: GET

- 参数说明:(headers)

|    参数    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   username    | string |  用户名 |

- 返回

|    名称    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   msg    | string | 返回信息 |
|   user_info    | json | 用户信息 |
|   lottery_info    | 数组 | 抽奖信息 |
|   gen_time    | string | 抽奖时间 |
|   lottery_name    | string | 抽奖名称 |
|   lottery_num    | int | 抽奖号 |
|   win    | int  | 是否中奖 0未中奖 1 中奖 |
|   user_id    | int | 用户ID |
|   username    | string | 用户名 |

- 实例

```
{
  "lottery_info": [
    {
      "gen_time": "20170611104620",
      "lottery_name": "mac_0611",
      "lottery_num": 1,
      "win": 0
    }
  ],
  "user_info": {
    "user_id": 2,
    "username": "kevin"
  }
  "msg": "success"
}
```

/lottery/ (POST)
---

- 功能: 创建新的抽奖

- 请求方法: POST

- 参数说明: (JSON)

|    参数    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   lotteryName    | string |  抽奖名称 |

- 返回

|    名称    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   msg    | string | 返回信息 |
|   lottery_name    | string | 抽奖名称 |

- 实例

```
{
  "lottery_name": "mac_0613",
  "msg": "success"
}
```

/lottery/ (GET)
---

- 功能: 进行一次抽奖

- 请求方法: GET

- 参数说明: (headers)

|    参数    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   username    | string |  用户名 |
|   lotteryName    | string |  抽奖名称 |

- 返回

|    名称    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   msg    | string | 返回信息 |
|   lottery_name    | string | 抽奖名称 |
|   lottery_num    | int | 抽奖号 |
|   user_id    | int | 用户ID |
|   username    | string | 用户名 |

- 实例

```
{
  "lottery_name": "mac_0613",
  "lottery_num": 50,
  "msg": "success",
  "user_id": 3,
  "username": "kevin1995"
}
```

/luckyNum/
---

- 功能: 开奖

- 请求方法: GET

- 参数说明: (headers)

|    参数    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   lotteryName    | string |  抽奖名称 |

- 返回

|    名称    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   msg    | string | 返回信息 |
|   lottery_name    | string | 抽奖名称 |
|   lottery_num   | int | 中奖号 |
|   lucky_user    | string | 幸运用户 |
|   user_id    | int | 用户ID |

- 实例

```
{
  "gen_time": "20170611164110",
  "lottery_name": "mac_0613",
  "lottery_num": 1,
  "lucky_user": "kevin1995",
  "user_id": 3
  "msg": "success"
}
```

/beatRatio/
---

- 功能: 用户抽奖击败比例

- 请求方法: GET

- 参数说明: (headers)

|    参数    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   lotteryName    | string |  抽奖名称 |
|   username    | string |  用户名 |

- 返回

|    名称    | 类型           | 说明  |
| ------------- |:-------------:| -----:|
|   msg    | string | 返回信息 |
|   lottery_name    | string | 抽奖名称 |
|   beat_ratio   | float | 击败比例 |
|   username    | string | 用户名 |

- 实例

```
{
  "beat_ratio": 0.333,
  "lottery_name": "mac_0611",
  "username": "kevin",
  "msg": "success"
}
```
