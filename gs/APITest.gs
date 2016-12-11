function postTestData(api, args) {
  if (!args) {
    var dummyDatas = dummyDataSheet.getRange(1, 1, dummyDataSheet.getLastRow(), 2).getValues();
    for (var i = 0; i < dummyDatas.length; i++) {
      if (dummyDatas[i][0] == api) {
        args = JSON.parse(dummyDatas[i][1]);
        doPost({parameter:{data:JSON.stringify({
          api: api,
          args: args})}});
      }
    }
  }
  else
  {  
    doPost({parameter:{data:JSON.stringify({
      api: api,
      args: args})}});
  }
}