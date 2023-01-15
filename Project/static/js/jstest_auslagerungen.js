///////////////////////////////////////////////////
///////////////// OLD KEYBOARD ////////////////////
///////////////////////////////////////////////////

//
//
// // let play_now = false;
// // const audioContext = new AudioContext();
//
// tonic = {
//     "C": 261.63,
//     "C#": 277.18,
//     "D": 293.66,
//     "D#": 311.13,
//     "E": 329.63,
//     "F": 349.23,
//     "F#": 369.99,
//     "G": 392.00,
//     "G#": 415.30,
//     "A": 440.00,
//     "A#": 466.16,
//     "B": 493.88
// };
// mode = {
//     "Major": [0, 2, 4, 5, 7, 9, 11], "Minor": [0, 2, 3, 5, 7, 8, 10],
//     "Pentatonic": [0, 2, 4, 7, 9], "Blues": [0, 3, 5, 6, 7, 10],
//     "Ionian": [0, 2, 4, 5, 7, 9, 11], "Dorian": [0, 2, 3, 5, 7, 9, 10],
//     "Phrygian": [0, 1, 3, 5, 7, 8, 10], "Lydian": [0, 2, 4, 6, 7, 9, 11],
//     "Mixolydian": [0, 2, 4, 5, 7, 9, 10], "Aeolian": [0, 2, 3, 5, 7, 8, 10],
//     "Locrian": [0, 1, 3, 5, 6, 8, 10], "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11],
//     "Melodic Minor": [0, 2, 3, 5, 7, 9, 11], "Whole Tone": [0, 2, 4, 6, 8, 10],
//     "Diminished": [0, 2, 3, 5, 6, 8, 9, 11], "Chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
//     "Major Pentatonic": [0, 2, 4, 7, 9], "Minor Pentatonic": [0, 3, 5, 7, 10],
//     "Major Blues": [0, 2, 3, 4, 7, 9], "Minor Blues": [0, 3, 5, 6, 7, 10]
// };
//
//
// // DEFAULT KEY
// let key = "C";
// let scale = "Major";
// let note_1 = {"note": "C", "frequency": tonic["C"]};
// let note_2 = {"note": "D", "frequency": tonic["D"]};
// let note_3 = {"note": "E", "frequency": tonic["E"]};
// let note_4 = {"note": "F", "frequency": tonic["F"]};
// let note_5 = {"note": "G", "frequency": tonic["G"]};
// let note_6 = {"note": "A", "frequency": tonic["A"]};
// let note_7 = {"note": "B", "frequency": tonic["B"]};
//
// oscillator_types = ["sine", "square", "sawtooth", "triangle"];
// let oscillator_type = oscillator_types[0];
//
// function playKick(static_url, kick) {
//     let path = static_url + "/kicks/" + kick;
//     let audio = new Audio(path);
//     audio.play();
// }
//
// function random_key() {
//     key = Object.keys(tonic)[Math.floor(Math.random() * Object.keys(tonic).length)];
//     scale = Object.keys(mode)[Math.floor(Math.random() * Object.keys(mode).length)];
//     document.querySelector("h1").innerHTML = "Key: " + key + " " + scale;
//     if (scale == "Major") {
//         for (let i = 0; i < 7; i++) {
//             note = Object.keys(tonic)[(Object.keys(tonic).indexOf(key) + mode[scale][i]) % 12];
//             document.querySelector("button:nth-child(" + (i + 3) + ")").innerHTML = note;
//         }
//     } else if (scale == "Minor") {
//         for (let i = 0; i < 7; i++) {
//             note = Object.keys(tonic)[(Object.keys(tonic).indexOf(key) + mode[scale][i]) % 12];
//             document.querySelector("button:nth-child(" + (i + 3) + ")").innerHTML = note;
//         }
//     } else if (scale == "Pentatonic") {
//         for (let i = 0; i < 5; i++) {
//             note = Object.keys(tonic)[(Object.keys(tonic).indexOf(key) + mode[scale][i]) % 12];
//             document.querySelector("button:nth-child(" + (i + 3) + ")").innerHTML = note;
//         }
//     } else if (scale == "Blues") {
//         for (let i = 0; i < 6; i++) {
//             note = Object.keys(tonic)[(Object.keys(tonic).indexOf(key) + mode[scale][i]) % 12];
//             document.querySelector("button:nth-child(" + (i + 3) + ")").innerHTML = note;
//         }
//     }
//
//     note_1 = {"note": key, "frequency": tonic[key]};
//     note_2 = {"note": key, "frequency": tonic[key] * Math.pow(2, mode[scale][1] / 12)};
//     note_3 = {"note": key, "frequency": tonic[key] * Math.pow(2, mode[scale][2] / 12)};
//     note_4 = {"note": key, "frequency": tonic[key] * Math.pow(2, mode[scale][3] / 12)};
//     note_5 = {"note": key, "frequency": tonic[key] * Math.pow(2, mode[scale][4] / 12)};
//     note_6 = {"note": key, "frequency": tonic[key] * Math.pow(2, mode[scale][5] / 12)};
//     note_7 = {"note": key, "frequency": tonic[key] * Math.pow(2, mode[scale][6] / 12)};
//     document.querySelector("button")[1].innerHTML = note_1.note;
//     document.querySelector("button")[2].innerHTML = note_2.note;
//     document.querySelector("button")[3].innerHTML = note_3.note;
//     document.querySelector("button")[4].innerHTML = note_4.note;
//     document.querySelector("button")[5].innerHTML = note_5.note;
//     document.querySelector("button")[6].innerHTML = note_6.note;
//     document.querySelector("button")[7].innerHTML = note_7.note;
// }
//
// function play(note) {
//     console.log(note);
//     const oscillator = audioContext.createOscillator();
//     oscillator.frequency.value = note.frequency;
//     oscillator.type = oscillator_type;
//     oscillator.connect(audioContext.destination);
//     oscillator.start();
//     setTimeout(() => {
//         oscillator.stop();
//     }, 500);
// }
//
// document.addEventListener('keydown', play_note);
//
// function play_note(event) {
//     if (event.key == "y") {
//         play(note_1);
//         document.querySelector("button:nth-child(3)").style.backgroundColor = "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
//     } else if (event.key == "x") {
//         play(note_2);
//         document.querySelector("button:nth-child(4)").style.backgroundColor = "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
//     } else if (event.key == "c") {
//         play(note_3);
//         document.querySelector("button:nth-child(5)").style.backgroundColor = "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
//     } else if (event.key == "v") {
//         play(note_4);
//         document.querySelector("button:nth-child(6)").style.backgroundColor = "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
//     } else if (event.key == "b") {
//         play(note_5);
//         document.querySelector("button:nth-child(7)").style.backgroundColor = "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
//     } else if (event.key == "n") {
//         play(note_6);
//         document.querySelector("button:nth-child(8)").style.backgroundColor = "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
//     } else if (event.key == "m") {
//         play(note_7);
//         document.querySelector("buttonm:nth-child(9)").style.backgroundColor = "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
//     }
// }
//
// function change_sound() {
//     oscillator_type = oscillator_types[(oscillator_types.indexOf(oscillator_type) + 1) % 4];
// }
//
//
// // -- SOUNDFONTS --
//
// let soundfont_instrument = 'acoustic_grand_piano';
// let soundfont_instruments = ['clavinet', 'acoustic_grand_piano', 'acoustic_guitar_nylon', 'acoustic_guitar_steel',
//     'electric_guitar_clean', 'electric_guitar_jazz', 'electric_guitar_muted', 'overdriven_guitar',
//     'distortion_guitar', 'guitar_harmonics', 'acoustic_bass', 'electric_bass_finger',
//     'electric_bass_pick', 'fretless_bass', 'slap_bass_1', 'slap_bass_2', 'synth_bass_1',
//     'synth_bass_2', 'violin', 'viola', 'cello', 'contrabass', 'tremolo_strings',
//     'pizzicato_strings', 'orchestral_harp', 'timpani', 'string_ensemble_1', 'string_ensemble_2',
//     'synth_strings_1', 'synth_strings_2', 'choir_aahs', 'voice_oohs', 'synth_voice', 'orchestra_hit',
//     'trumpet', 'trombone', 'tuba', 'muted_trumpet', 'french_horn', 'brass_section', 'synth_brass_1',
//     'synth_brass_2', 'soprano_sax', 'alto_sax', 'tenor_sax', 'baritone_sax', 'oboe', 'english_horn',
//     'bassoon', 'clarinet', 'piccolo', 'flute', 'recorder', 'pan_flute', 'blown_bottle', 'shakuhachi',
//     'whistle', 'ocarina', 'lead_1_square', 'lead_2_sawtooth', 'lead_3_calliope', 'lead_4_chiff',
//     'lead_5_charang', 'lead_6_voice', 'lead_7_fifths', 'lead_8_bass__lead', 'pad_1_new_age',
//     'pad_2_warm', 'pad_3_polysynth', 'pad_4_choir', 'pad_5_bowed', 'pad_6_metallic', 'pad_7_halo',
//     'pad_8_sweep', 'fx_1_rain', 'fx_2_soundtrack', 'fx_3_crystal', 'fx_4_atmosphere', 'fx_5_brightness']
//
// function change_soundfont_instrument() {
//     console.log("change_soundfont_instrument");
//     soundfont_instrument = soundfont_instruments[Math.floor(Math.random() * soundfont_instruments.length)];
//     document.querySelector("h4").innerHTML = soundfont_instrument;
//     Soundfont.instrument(audioContext, soundfont_instrument).then(function (instrument) {
//         soundfont_instrument = instrument;
//     });
// }
//
// function play_soundfont() {
//     // console.log("play_c4");
//     // play(note_1);
//     console.log("play_soundfont");
//     Soundfont.instrument(audioContext, soundfont_instrument).then((instrument) => {
//         instrument.play('C4');
//     });
// }

// var static_url = '{{ static_url }}'
//
// kick_sample_name = document.querySelector('#kick_sample_name')
//
//
// tone_module.addEventListener('load', function () {
//
//     gallery_item_btn_list = document.querySelectorAll('.gallery_items')
//
//     const drum_samples = [
//         new Tone.Player("{{static_url}}/kicks/BOS_DHT_Kick_One_Shot_Rumble_Massive.wav").toDestination(),
//         new Tone.Player("{{static_url}}/snares/ff_bt_snare_one_shot_low_rud.wav").toDestination(),
//         new Tone.Player("{{static_url}}/hihats/KSHMR_Acoustic_Closed_Hat_04_Clean.wav").toDestination(),
//         new Tone.Player("{{static_url}}/kicks/BOS_DHT_Kick_One_Shot_Rumble_Thud.wav").toDestination()
//     ];
//
//     // For changing Sample: Event Listener for all gallery items
//     for (let i = 0; i < gallery_item_btn_list.length; i++) {
//         gallery_item_btn_list[i].addEventListener('click', initializeSamples(i))
//     }
//
//     // For changing Sample: New Initialization of Samples
//     function initializeSamples(i) {
//         console.log('initializeSamples()')
//         // const drum_samples = []
//         // for (let i = 0; i < 4; i++) {
//         //     drum_samples.push(new Audio())
//         // }
//         drum_samples[0].src = static_url + 'kicks/' + {
//         {
//             kick_paths[i]
//         }
//     }
//
//         console.log(drum_samples[0].src)
//         // drum_samples[1].src = static_url + 'snares/' + snare_names[0]
//         // drum_samples[2].src = static_url + 'hihats/' + hihat_names[0]
//         // drum_samples[3].src = static_url + 'perc/' + perc_names[0]
//     }
//
//     const synths = [
//         new Tone.Synth().toDestination(),
//         new Tone.Synth().toDestination(),
//         new Tone.Synth().toDestination(),
//         new Tone.Synth().toDestination()
//     ];
//
//
//     initializeSamples()
//
//     synths[0].oscillator.type = "sine";
//     synths[1].oscillator.type = "triangle";
//     synths[2].oscillator.type = "sawtooth";
//     synths[3].oscillator.type = "square";
//
//
//     synths.forEach(synth => synth.toMaster());
//
//     // const $rows = document.querySelectorAll(".sequencer-row"), notes = ["G5", "A5", "B5", "A3"];
//     const $rows = document.querySelectorAll(".sequencer-row"), notes = ["C4", "C4", "C4", "C4"];
//
//     console.log($rows);
//     let index = 0;
//
//     // repeated event every 8th note
//     Tone.Transport.scheduleRepeat(repeat_drum_samples, "16n");
//     Tone.Transport.bpm.value = 140;
//     Tone.Transport.start();
//
//     function play_note_with_tone_js() {
//         Tone.start();
//         Tone.Transport.toggle();
//     }

   var tone_module = document.querySelector('#tone_module')

   ///////////////////////////////////////////////////
   ///////////////// KEYBOARD ////////////////////////
   ///////////////////////////////////////////////////

   const synth = new Tone.Synth();
   synth.oscillator.type = "sine";
   synth.toMaster();

   const piano = document.getElementById("piano");

   piano.addEventListener("mousedown", e => {
       synth.triggerAttack(e.target.dataset.note);
   });

   piano.addEventListener("mouseup", e => {
       synth.triggerRelease();
   });

   // Key Down and its function

   function keyDown(note) {
       console.log(note);
       document.querySelector('[data-note=' + CSS.escape(note) + ']').classList.add("active");
       synth.triggerAttack(note);
   }

   document.addEventListener("keydown", e => {
       switch (e.key) {
           // Create a case for each key in a for loop
           case "d":
               keyDown("C4");
           case "r":
               keyDown("C#4");
           case "f":
               keyDown("D4");
           case "t":
               keyDown("D#4");
           case "g":
               keyDown("E4");
           case "h":
               keyDown("F4");
           case "u":
               keyDown("F#4");
           case "j":
               keyDown("G4");
           case "i":
               keyDown("G#4");
           case "k":
               keyDown("A4");
           case "o":
               keyDown("A#4");
           case "l":
               keyDown("B4");
           default:
               "none";
       }
   });

   // Key Up and its function

   function keyUp(note) {
       document.querySelector('[data-note=' + CSS.escape(note) + ']').classList.remove("active");
       synth.triggerRelease();
   }

   document.addEventListener("keyup", e => {
       switch (e.key) {
           case "d":
               keyUp("C4");
           case "r":
               keyUp("C#4");
           case "f":
               keyUp("D4");
           case "t":
               keyUp("D#4");
           case "g":
               keyUp("E4");
           case "h":
               keyUp("F4");
           case "u":
               keyUp("F#4");
           case "j":
               keyUp("G4");
           case "i":
               keyUp("G#4");
           case "k":
               keyUp("A4");
           case "o":
               keyUp("A#4");
           case "l":
               keyUp("B4");
           default:
               console.log("Key not found");
       }
   });