function testOfferPlaylog() {
  postTestData("offer_playlog", {
    friendCode: 0,
    displayRate: 0,
    bestRate: 0,
    log: [
      {
        musicName:"Test",
        levelName:"basic",
        score:500000
      },
      {
        musicName:"Test",
        levelName:"advanced",
        score:975000
      },
      {
        musicName:"Test",
        levelName:"expert",
        score:1000000
      },
      {
        musicName:"Test",
        levelName:"master",
        score:1007500
      }]
  });
}