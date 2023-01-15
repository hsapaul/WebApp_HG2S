var tone_module = document.querySelector('#tone_module');

tone_module.addEventListener('click', function () {

    console.log("dreck");

    const synth = new Tone.Synth();
    synth.oscillator.type = "sine";
    synth.toMaster();

    const piano = document.getElementById("piano");

    note_elements = piano.querySelectorAll(".key");

    note_elements.forEach(function (note_element) {
        note_element.addEventListener("click", function () {
            console.log(note_element.dataset.note);
            synth.triggerAttackRelease(note_element.dataset.note, "8n");
        });

});


// piano.addEventListener("mousedown", e => {
//   synth.triggerAttack(e.target.dataset.note);
// });
//
// piano.addEventListener("mouseup", e => {
//   synth.triggerRelease();
// });
//
// document.addEventListener("keydown", e => {
//   switch (e.key) {
//     case "d":
//       console.log("d");
//       return synth.triggerAttack("C4");
//     case "r":
//       return synth.triggerAttack("C#4");
//     case "f":
//       return synth.triggerAttack("D4");
//     case "t":
//       return synth.triggerAttack("D#4");
//     case "g":
//       return synth.triggerAttack("E4");
//     case "h":
//       return synth.triggerAttack("F4");
//     case "u":
//       return synth.triggerAttack("F#4");
//     case "j":
//       return synth.triggerAttack("G4");
//     case "i":
//       return synth.triggerAttack("G#4");
//     case "k":
//       return synth.triggerAttack("A4");
//     case "o":
//       return synth.triggerAttack("A#4");
//     case "l":
//       return synth.triggerAttack("B4");
//     default:
//       return;
//   }
// });
//
// document.addEventListener("keyup", e => {
//   switch (e.key) {
//     case "d":
//     case "r":
//     case "f":
//     case "t":
//     case "g":
//     case "h":
//     case "u":
//     case "j":
//     case "i":
//     case "k":
//     case "o":
//     case "l":
//       synth.triggerRelease();
//   }
// });
})
;