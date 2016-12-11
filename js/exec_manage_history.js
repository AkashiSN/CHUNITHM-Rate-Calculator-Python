try {
    gas_manage_history(
        function (d) {
            var data = d.result;
            var recent_candidate_list = data.recentCandidate;
            alert(recent_candidate_list.map(function (p) {
                return p.name + ":(" + p.score + "," + p.rate + ")";
            }).reduce(function (prev, curr) {
                return prev + "\n" + curr;
            }));

            var recent_list = data.recent;
            var ave = recent_list
                .map(function (p) { return p.rate; })
                .reduce(function (prev, curr) { return prev + curr; }) / 10;
            ave = Math.floor(ave * 100) / 100;
            alert("Recent値 : " + ave + "\nRecent枠内訳\n" +
                recent_list.map(function (p) {
                    return p.name + ":(" + p.score + "," + p.rate + ")";
                }).reduce(function (prev, curr) {
                    return prev + "\n" + curr;
                }));
        },
        function (id) { alert("エラー : " + id); });
}
catch (e) {
    alert("動作が停止しました。次に出てくるアラートメッセージを開発者にお知らせください。");
    alert("例外 : " + e.name + "\n内容 : " + e.message);
}