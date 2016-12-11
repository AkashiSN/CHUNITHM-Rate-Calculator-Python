function testAddMusicData() {
  postTestData("add_music_data", {
    musicData: [{
      id: 0,
      name: "Test",
      level: [
        {constant: 1, checked: false},
        {constant: 4, checked: false},
        {constant: 7, checked: false},
        {constant: 11.3, checked: true}
      ]
    }]
  });
}