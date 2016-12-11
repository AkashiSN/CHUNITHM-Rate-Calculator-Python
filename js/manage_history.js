// GetUserInfoApi
// {
//   userId,
//   userInfo:{
//     characterFileName,
//     characterLevel,
//     friendCount,
//     highestRating,
//     level,
//     playCount,
//     playerRating,
//     point,
//     reincarnationNum,
//     totalPoint,
//     trophyName,
//     trophyType,
//     userName,
//     webLimitDate,
//   },
// }

// GetUserFriendlistApi
// {
//   acceptCount,
//   friendCode,
//   length,
//   userFriendlistList: [{
//     friendCode,
//     isFavorite,
//     orderId,
//   }],
//   userId,
// }

// GetUserPlaylogApi Result
// {
//   length,
//   uesrId,
//   userPlaylogList: [{
//     fullChainKind,
//     isAllJustice,
//     isClear,
//     isFullCombo,
//     isNewRecord,
//     levelName,
//     musicFileName,
//     musicName,
//     orderId,
//     playKind,
//     rank,
//     score,
//     track,
//     userPlayData,
//   ]}
// }

// GetUserMusicApi
// {
//   characterFileName,
//   characterLevel,
//   genreList,
//   genreMap,
//   length,
//   musicNameMap,
//   userId,
//   userMusicList: [{
//     fullChain,
//     isAllJustice,
//     isFullCombo,
//     isSuccess,
//     level,
//     musicId,
//     playCount,
//     scoreMax,
//     scoreRank,
//     updateDate,
//   }],
//   userName,
// }

function gas_manage_history(callback, req_errorback, send_errorback) {
    function requests_api(api_req_group, callback, errorback, result) {
        if (!result) {
            result = new Array();
        }
        if (api_req_group.length > 0) {
            request_api(api_req_group[0].api_name, api_req_group[0].req_data,
                function (res_data) {
                    result.push(res_data);
                    api_req_group.shift();
                    requests_api(api_req_group, callback, errorback, result);
                }, errorback);
        }
        else {
            callback && callback(result);
        }
    }

    function encode_user_info(user_info_source) {
        var user_info = new Object();
        user_info.playerRating = user_info_source.userInfo.playerRating;
        return user_info;
    }

    function encode_friendlist(friendlist_source) {
        var friendlist = new Object();
        friendlist.friendCode = friendlist_source.friendCode;
        return friendlist;
    }

    function encode_playlog(playlog_source) {
        return playlog_source.userPlaylogList.map(function (log) {
            return {
                musicName: encodeURIComponent(log.musicName),
                levelName: log.levelName,
                score: log.score,
                userPlayDate: log.userPlayDate
            }
        }).reverse();
    }

    function encode_record(basic, advanced, expert, master) {

        function get_id_map(list) {
            var genre_list = list.genreList;
            var music_list = list.userMusicList;
            var id_map = new Object();
            for (var i = 0; i < genre_list.length; i++) {
                var id = genre_list[i];
                for (var j = 0; j < music_list.length; j++) {
                    if (music_list[j].musicId == id) {
                        id_map[id.toString(10)] = j;
                        break;
                    }
                }
            }
            return id_map;
        }

        var record = new Array();
        var genre_list = basic.genreList;
        var music_list = basic.userMusicList;

        var basic_id_map = get_id_map(basic);
        var advanced_id_map = get_id_map(advanced);
        var expert_id_map = get_id_map(expert);
        var master_id_map = get_id_map(master);

        for (var i = 0; i < genre_list.length; i++) {
            var id = genre_list[i];
            var key = id.toString(10);
            var basic_data = basic.userMusicList[basic_id_map[key]];
            var advanced_data = advanced.userMusicList[advanced_id_map[key]];
            var expert_data = expert.userMusicList[expert_id_map[key]];
            var master_data = master.userMusicList[master_id_map[key]];
            record.push({
                musicId: id,
                score: [
                    basic_data ? basic_data.scoreMax || 0 : 0,
                    advanced_data ? advanced_data.scoreMax || 0 : 0,
                    expert_data ? expert_data.scoreMax || 0 : 0,
                    master_data ? master_data.scoreMax || 0 : 0]
            });
        }

        return record.sort(function (r1, r2) { return r1.musicId - r2.musicId; });
    }

    requests_api([
        { api_name: "GetUserInfoApi", req_data: { friendCode: 0, fileLevel: 1 } },
        { api_name: "GetUserFriendlistApi", req_data: { state: 4 } },
        { api_name: "GetUserPlaylogApi", req_data: {} },
        { api_name: "GetUserMusicApi", req_data: { level: "19900" } },
        { api_name: "GetUserMusicApi", req_data: { level: "19901" } },
        { api_name: "GetUserMusicApi", req_data: { level: "19902" } },
        { api_name: "GetUserMusicApi", req_data: { level: "19903" } },
    ],
    function (result) {
        var req_data = new Object();
        req_data.playerRating = encode_user_info(result[0]).playerRating;
        req_data.friendCode = encode_friendlist(result[1]).friendCode;
        req_data.playlog = encode_playlog(result[2]);
        req_data.record = encode_record(result[3], result[4], result[5], result[6]);
        gas_request_api("manage_history", req_data, callback, send_errorback);
    },
    req_errorback);
}