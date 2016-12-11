// プレイ履歴を管理するAPI
function manageHistory(args) {
  var header = [
    "ID",
    "表示レート",
    "単曲レート値",
    "譜面定数",
    "スコア",
    "楽曲ID", 
    "楽曲名",
    "難易度",
    "B合計値",
    "R合計値", 
    "推測R合計値",
    "誤差",
    "レコード",
    "Best枠",
    "推測Recent枠", 
    "推測Recent候補枠",
    "プレイ日時",
    "データ追加日時",
    "バージョン"];
  
  // シートの初期化
  function formatSheet(sheet) {
    outputLog(["insert sheet"]);
    sheet.getRange(1, 1, 1, header.length).setValues([header]);
    return sheet;
  }
  
  // シートの作成・取得
  var hash = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_1, args.friendCode);
  var sheetName = bytes_to_hex_string(hash);  
  var userDataSheet = playHistoryBook.getSheetByName(sheetName) || formatSheet(playHistoryBook.insertSheet(sheetName));
  
  // データ準備
  var data = new Array();
  var addedDate = new Date();
  var lastIndex = userDataSheet.getLastRow();
  var lastRowData = new Array();
  if (lastIndex > 1) {
    lastRowData = userDataSheet.getRange(lastIndex, 1, 1, header.length).getValues()[0];
  }
  var lastPlayDate = (lastIndex > 1) ? new Date(lastRowData[16]) : new Date(0);
  var index = lastIndex - 1;
  var playerRating = parseFloat(args.playerRating) / 100;
  var recentCandidate = (lastIndex > 1) ? JSON.parse(lastRowData[15]) : instantiateRecentCandidate();
  
  // バージョンチェック
  if (!lastRowData[18] || lastRowData[18] < Version) {
    recentCandidate = updateRecentCandidate(recentCandidate);
  }
  
  // キャッシュ
  var recordJson = JSON.stringify(args.record);
  var best = getBest(args.record);
  var bestJson = JSON.stringify(best);
  
  function getPlayerRatingCell(index) { return "B" + index; }
  function getConstantCell(index) { return "D" + index; }
  function getScoreCell(index) { return "E" + index; }
  function getBestRatingSumCell(index) { return "I" + index; }
  function getRecnetRatingSumCell(index) { return "J" + index; }
  function getGuessRecentRatingSum(index) { return "K" + index; }
  function getRecordCell(index) { return "M" + index; }
  function getBestCell(index) { return "N" + index; }
  function getRecentCell(index) { return "O" + index; }
  function getRecentCandidateCell(index) { return "P" + index; }
  function getAddedDateCell(index) { return "R" + index; }
  function getVersionCell(index) { return "S" + index; }
  
  function concatArgs(args) {
    return args.reduce(function (prev, current) { return prev + "," + current; });
  }
  
  var added = new Array();
  for (var i = 0; i < args.playlog.length; i++) {
    
    var dateInfo = /(\d{4})[-\/](\d{2})[-\/](\d{2}) (\d{1,2}):(\d{2}):(\d{2}).\d*/.exec(args.playlog[i].userPlayDate);
    var playDate = new Date(dateInfo[1], parseInt(dateInfo[2]) - 1, dateInfo[3], dateInfo[4], dateInfo[5], dateInfo[6]);
    if (playDate.getTime() > lastPlayDate.getTime()) {
      var log = new Object();  
      log.id = musicDataValue[musicNameMap[args.playlog[i].musicName]][0];
      log.name = args.playlog[i].musicName;
      log.level = levelNameToLevelMap[args.playlog[i].levelName];
      log.constant = musicDataValue[musicNameMap[log.name]][2+log.level];
      log.score = args.playlog[i].score;
      log.rate = getPlayRating(log.constant, log.score);
      log.playDateTime = playDate.getTime();
      
      if (log.level != 4) {
        recentCandidate = simulateRecentTransition(recentCandidate, log);
      }
      
      var isLastRow = i === args.playlog.length - 1;
      var row = new Object();
      row["ID"] = ++index;
      row["PlayerRating"] = isLastRow ? playerRating : "=" + getPlayerRatingCell(index + 2);
      row["MusicId"] = log.id;
      row["MusicName"] = "=\"" + log.name + "\"";
      row["Level"] = log.level;
      row["Constant"] = log.constant;
      row["Score"] = log.score;
      row["PlayRating"] = "=getPlayRating(" + concatArgs([getConstantCell(index + 1), getScoreCell(index + 1)]) + ")";
      row["BestRatingSum"] = "=getRating(" + getBestCell(index + 1) + ")";
      row["RecentRatingSum"] = "=40*" + getPlayerRatingCell(index + 1) + "-" + getBestRatingSumCell(index + 1);
      row["GuessRecentRatingSum"] = "=getRating(" + getRecentCell(index + 1) + ")"
      row["Error"] = "=" + getRecnetRatingSumCell(index + 1) + "-" + getGuessRecentRatingSum(index + 1);
      row["Record"] = isLastRow ? recordJson : "=" + getRecordCell(index + 2);
      row["Best"] = isLastRow ? bestJson : "=" + getBestCell(index + 2);
      row["Recent"] = "=getRecent(" + getRecentCandidateCell(index + 1) + ")";
      row["RecentCandidate"] = JSON.stringify(recentCandidate);
      row["PlayDate"] = args.playlog[i].userPlayDate;
      row["AddedDate"] = isLastRow ? addedDate : "=" + getAddedDateCell(index + 2);
      row["Version"] = isLastRow ? Version : "=" + getVersionCell(index + 2);
      
      data.push([
        row["ID"],
        row["PlayerRating"],
        row["PlayRating"],
        row["Constant"],
        row["Score"],
        row["MusicId"],
        row["MusicName"],
        row["Level"],
        row["BestRatingSum"],
        row["RecentRatingSum"],
        row["GuessRecentRatingSum"],
        row["Error"],
        row["Record"],
        row["Best"],
        row["Recent"],
        row["RecentCandidate"],
        row["PlayDate"],
        row["AddedDate"],
        row["Version"]]);
      
      added.push(index);
    }
  }
  
  // 書き込み
  var rowLength = data.length;
  var columnLength = header.length;
  if (rowLength >= 1) {
    userDataSheet.getRange(lastIndex + 1, 1, rowLength, columnLength).setValues(data);
  }
  
  return {added:added, best:best, recent:getRecent(recentCandidate), recentCandidate: recentCandidate};
}

// Recent候補枠のデータ更新
function updateRecentCandidate(recentCandidate) {  
  return recentCandidate.map(function (p) {
    var name = p.musicName || p.name;
    var id = p.id || (name && musicDataValue[musicNameMap[name]][0]);
    var level = p.level || levelNameToLevelMap[p.levelName];
    var constant = p.constant || (name && musicDataValue[musicNameMap[name]][level+2]) || 0;
    return {
      id: id,
      name: name,
      level: level,
      constant: p.constant,
      score: p.score,
      rate: p.rate,
      playDateTime: p.playDateTime
    };
  });
}