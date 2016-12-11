var levelNameToLevelMap = {
  basic: 0,
  advance: 1,
  expert: 2,
  master: 3,
  worldsend: 4,
};

// 楽曲表
var musicDataBook = SpreadsheetApp.openById("1tKuY9WoakgoUhR6PXaxMubCiGlCelHNr4nRDXpSrFQU");
var musicDataSheet = musicDataBook.getSheetByName("MusicData");
var musicDataValue = [[]];
{
  var rowLength = musicDataSheet.getLastRow() - 1;
  var columnLength = 13;
  if (rowLength > 0) {
    musicDataValue = musicDataSheet.getRange(2, 1, rowLength, columnLength).getValues();
  }
}

var musicIdMap = new Object();
var musicNameMap = new Object();
for (var i = 0; i < musicDataValue.length; i++) {
  musicIdMap[musicDataValue[i][0].toString(10)] = i;
  musicNameMap[musicDataValue[i][1]] = i;
}

// プレイ履歴提供
var offerPlaylogBook = SpreadsheetApp.openById("1HV6PSbJYM1-hLD-qMChs8P4nxqSyhpoPS5oIFUdbkKw");
var offerPlaylogSheets = [offerPlaylogBook.getSheetByName("Playlog")];

// デバッグ
var debugBook = SpreadsheetApp.openById("1nHxaNXK8URIlo-EZWi9fAxuxgVHRanKnRgx5tnUUKw0");
var logSheet = debugBook.getSheetByName("Log");
var dummyDataSheet = debugBook.getSheetByName("DummyData");

// プレイ履歴表
var playHistoryBook = SpreadsheetApp.openById("17FgFHz0kqEGmV_4f2un3-gwKCMILZlQVpkEjmtSwcIM");

// バイト値を16進文字列に変換
function byte_to_hex (byte_num) {
  var digits = (byte_num & 0xff).toString(16);
  if ((byte_num & 0xff) < 16) return '0' + digits;
  return digits;
}

// バイト配列を16進文字列に変換
function bytes_to_hex_string (bytes) {
  var	result = "";
  for (var i = 0; i < bytes.length; i++) {
    result += byte_to_hex(bytes[i]);
  }
  return result;
}

// ログ出力
var debug = false;
function outputLog(data, insertDate) {
  if (!debug) {
    return;
  }
  
  var row = new Array();
  if (insertDate) {
    row.push(new Date());
  }
  else {
    row.push("");
  }
  
  row = row.concat(data);
  logSheet.appendRow(row);
}

var border = [
  { score: 500000, rate: function(c) { return 0; } },
  { score: 800000, rate: function(c) { return (c >= 6) ? (c - 5) / 2 : 0; } },
  { score: 900000, rate: function(c) { return (c >= 6) ? (c - 5) : 0; } },
  { score: 925000, rate: function(c) { return (c >= 4) ? (c - 3) : 0; } },
  { score: 975000, rate: function(c) { return c; } },
  { score: 1000000, rate: function(c) { return c + 1; } },
  { score: 1005000, rate: function(c) { return c + 1.5; } },
  { score: 1007500, rate: function(c) { return c + 2; } }];

// 単曲レート値算出
function getPlayRating(musicConstant, score) {
  if (musicConstant < 1) {
    return 0;
  }
  
  if (score < border[0].score) {
    return 0;
  }
  else if(score >= border[border.length - 1].score) {
    return musicConstant + 2;
  }
  
  var rate = 0;
  for (var i = 0; i < border.length - 1; i++) {
    var ratio = Math.min(Math.max((score - border[i].score) /  (border[i + 1].score - border[i].score), 0), 1);
    var deltaRate = Math.max(border[i + 1].rate(musicConstant) - border[i].rate(musicConstant), 0);
    rate += ratio * deltaRate;
  }
  
  return Math.floor(rate * 100) / 100; 
}

// 楽曲情報取得
function getMusicData(musicName) {
  if (musicNameMap[musicName] !== undefined && musicDataValue[musicNameMap[musicName]]) {
    var musicData = musicDataValue[musicNameMap[musicName]];
    return {
      id: musicData[0],
      name: musicName,
      constant:[
        musicData[2],
        musicData[3],
        musicData[4],
        musicData[5],
        0]
    };
  }
  
  return {
    id: -1,
    name: musicName,
    constant:[0,0,0,0,0]
  };
}

// Best枠抽出
function getBest(record) {
  var best = new Array();
  for (var i = 1; i < record.length; i++){
    for (var j = 0; j < musicDataValue.length; j++) {
      if (musicDataValue[j][0] == record[i].musicId) {
        for (var k = 0; k < 4; k++) {
          best.push({ id:musicDataValue[j][0], name:musicDataValue[j][1], level: k, constant: musicDataValue[j][2+k], score: record[i].score[k] || 0, rate: getPlayRating(musicDataValue[j][2+k], record[i].score[k] || 0) });
        }
      }
    }
  }
  
  best.sort(function(b1, b2) { return (b1.rate !== b2.rate) ? (b2.rate - b1.rate) : (b2.constant - b1.constant); });
  return best.slice(0, 30);
}

// 初期Recent候補枠生成
function instantiateRecentCandidate() {
  var recentCandidate = new Array();
  for (var i = 0; i < 30; i++) {
    recentCandidate.push({ score: 0, rate: 0, playDateTime: 0 });
  }
  
  return recentCandidate;
}

// Recent枠の抽出
function getRecent(recentCandidate) {
  return [].concat(recentCandidate).sort(function (p1, p2) {
    return (p1.rate !== p2.rate) ? (p2.rate - p1.rate) : (p1.playDateTime - p2.playDateTime);
  }).slice(0, 10);
}

// Recent候補枠の遷移
function simulateRecentTransition(recentCandidate, playlog) {
  var result = [].concat(recentCandidate);
  var recent = getRecent(recentCandidate);
  // 第1法則 最新単曲レート値を下回る一番古い楽曲
  if (playlog.rate > Math.min.apply(null, recent.map(function (p) { return p.rate; }))) {
    for (var i = 0; i < result.length; i++) {
      if (playlog.rate > result[i].rate) {
        result.splice(i, 1);
        result.push(playlog);
        break;
      }
    }
  }
  // 第2法則 最新楽曲
  else if (playlog.score >= 1007500 || playlog.score >= Math.min.apply(null, recent.map(function (p) { return p.score; }))) {
    // 何もしないに等しい
  }
  // 第3法則 一番古い楽曲
  else {
    result.shift();
    result.push(playlog);
  }
  
  return result;
}