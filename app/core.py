from flask import request, g
from datetime import datetime
from . import app, jsonify, query_db, alter_db, get_user_info
from config import CNSESH, CNSESZ
import sqlite3


def get_market_index():
    return CNSESH * CNSESZ


@app.route('/user/', methods=['GET', 'POST'])
def user_about():
    if request.method == 'GET':
        username = request.headers.get('username')
        if not username:
            return jsonify(msg='传参有误')
        user_res = get_user_info(g.db, username)
        if user_res == -1:
            return jsonify(msg='用户名不存在')
        user_id, username = user_res
        lottery_first_res = query_db(g.db,
                                     "SELECT USERLOTTERY.LOTTERY_NAME, USERLOTTERY.LOTTERY_ID"
                                     " FROM USER INNER JOIN USERLOTTERY ON USER.ID = USERLOTTERY.USER_ID"
                                     " WHERE USERNAME = '%s';"
                                     % username)
        lottery_info = []
        for lottery in lottery_first_res:
            lottery_res = query_db(g.db, "SELECT * FROM '%s' WHERE id = %d" % (lottery[0], lottery[1]))
            lottery_info.append({
                'lottery_name': lottery[0],
                'lottery_num': lottery_res[0][0],
                'gen_time': lottery_res[0][1],
                'win': lottery_res[0][2]
            })
        user_info = {'user_id': user_id, 'username': username}
        return jsonify(user_info=user_info, lottery_info=lottery_info, msg='success')
    elif request.method == 'POST':
        if not request.json:
            return jsonify(msg='传参有误')
        username = request.json.get('username')
        if not username:
            return jsonify(msg='用户名错误')
        lastrowid = alter_db(g.db,
                             "INSERT INTO USER (USERNAME) "
                             "SELECT '%s' WHERE NOT EXISTS (SELECT * FROM USER WHERE USERNAME = '%s');"
                             % (username, username))
        if lastrowid == 0:
            return jsonify(msg='用户名已经存在')
        return jsonify(user_id=lastrowid, username=username, msg='success')


@app.route('/lottery/', methods=['GET', 'POST'])
def lottery_about():
    if request.method == 'GET':
        if not request.headers:
            return jsonify(msg='参数错误')
        username = request.headers.get('username')
        lottery_name = request.headers.get('lotteryName')
        if not username or not lottery_name:
            return jsonify(msg='参数错误')
        user_res = get_user_info(g.db, username)
        if user_res == -1:
            return jsonify(msg='用户不存在')
        is_finished = query_db(g.db, "SELECT COUNT(*) FROM '%s' WHERE WIN = 1;" % lottery_name)[0][0]
        if is_finished > 0:
            return jsonify(msg='抽奖结束')
        try:
            # 插入数据
            user_id = user_res[0]
            rowid = alter_db(g.db, "INSERT INTO '%s' (GEN_TIME, WIN) VALUES('%s', 0);"
                             % (lottery_name, datetime.today().strftime("%Y%m%d%H%M%S")))
        except sqlite3.OperationalError as e:
            return jsonify(msg='该抽奖活动不存在')
        if rowid == 0:
            return jsonify(msg='抽奖失败')
        rowid = alter_db(g.db,
                         "INSERT INTO USERLOTTERY (USER_ID, LOTTERY_ID, LOTTERY_NAME) VALUES (%d, %d, '%s');"
                         % (user_id, rowid, lottery_name))
        if rowid == 0:
            return jsonify(msg='抽奖失败')
        return jsonify(lottery_num=rowid, lottery_name=lottery_name, username=username, user_id=user_id, msg='success')
    elif request.method == 'POST':
        if not request.json:
            return jsonify(msg='参数错误')
        lottery_name = request.json.get('lotteryName')
        if not lottery_name:
            return jsonify(msg='参数错误')
        create_lottery_table_sql = "CREATE TABLE IF NOT EXISTS {} " \
                                   "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, GEN_TIME TEXT NOT NULL," \
                                   " WIN INTEGER NOT NULL);" \
                                   .format(lottery_name)
        create_index_sql = "CREATE INDEX IF NOT EXISTS WIN_INDEX ON {} (WIN)".format(lottery_name)
        alter_db(g.db, create_lottery_table_sql)
        alter_db(g.db, create_index_sql)
        return jsonify(lottery_name=lottery_name, msg='success')


@app.route('/luckyNum/', methods=['GET'])
def lucky_num():
    if not request.headers:
        return jsonify(msg='参数错误')
    lottery_name = request.headers.get('lotteryName')
    if not lottery_name:
        return jsonify(msg='参数错误')
    try:
        is_finished = query_db(g.db, "SELECT COUNT(*) FROM '%s' WHERE WIN = 1;" % lottery_name)[0][0]
        if is_finished > 0:
            raise Exception("已经抽过奖")
    except Exception as e:
        return jsonify(msg='没有这个抽奖')
    lottery_count = query_db(g.db, "SELECT COUNT(*) FROM '%s';" % lottery_name)[0][0]
    lucky_mid_num = int(str(int(get_market_index() * 10000))[::-1])
    lucky_number = (lucky_mid_num % lottery_count) + 1
    lucky_user_sql = "SELECT USER.ID, USER.USERNAME, {0}.GEN_TIME, USERLOTTERY.LOTTERY_ID FROM USERLOTTERY" \
                     " INNER JOIN USER ON USERLOTTERY.USER_ID = USER.ID INNER JOIN {0} ON {0}.ID = {1}" \
                     " WHERE LOTTERY_NAME = '{0}' AND LOTTERY_ID = {1}".format(lottery_name, lucky_number)
    lucky_user_info = query_db(g.db, lucky_user_sql)
    # 将win设置为1
    set_win_sql = "UPDATE {} SET WIN = 1 WHERE ID = {}".format(lottery_name, lucky_number)
    alter_db(g.db, set_win_sql)
    return jsonify(lottery_name=lottery_name, user_id=lucky_user_info[0][0], lucky_user=lucky_user_info[0][1],
                   gen_time=lucky_user_info[0][2], lottery_num=lucky_user_info[0][3], msg="success")


@app.route('/beatRatio/', methods=['GET'])
def get_beat_ratio():
    if not request.headers:
        return jsonify(msg='参数错误')
    lottery_name = request.headers.get('lotteryName')
    username = request.headers.get('username')
    if not lottery_name or not username:
        return jsonify(msg='参数错误')

    user_rank_sql = "SELECT USERNAME FROM USERLOTTERY INNER JOIN USER ON USER_ID = USER.ID" \
                    " WHERE LOTTERY_NAME = '%s' GROUP BY USERNAME ORDER by COUNT(*)" % lottery_name
    user_ranks = query_db(g.db, user_rank_sql)
    try:
        user_index = user_ranks.index((username, ))
        user_ranks_len = len(user_ranks)
        if user_index == user_ranks_len - 1:
            beat_ratio = 1
        else:
            beat_ratio = round(user_index / user_ranks_len, 3)
    except Exception as e:
        return jsonify(msg='没有找到该用户或者没有该抽奖')
    return jsonify(beat_ratio=beat_ratio, username=username, lottery_name=lottery_name, msg='success')
