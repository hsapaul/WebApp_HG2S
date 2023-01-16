import {Tone} from "tone/Tone/core/Tone";

function startSequencer() {
    initializeSamples();

}

function initializeSamples() {
    // query selector all buttons inside the draggables class
    var select_drum_samples = document.querySelectorAll(".draggables");

    const drum_samples = [
        new Tone().Player(),
        new Tone().Player(),
        new Tone().Player(),
        new Tone().Player(),
    ]

    for (var i = 0; i < select_drum_samples.length; i++) {
        // if element has button as a child
        if (select_drum_samples[i].querySelector("button")) {
            var element_name = select_drum_samples[i].innerText;
            // console.log(i, element_name);
            drum_samples[i].load(element_name);
        }
    }

    for (var i = 0; i < drum_samples.length; i++) {
        drum_samples[i].toMaster();
    }

}


//     const drum_samples = [
//         new Tone().Player("static/samples/808_kick.wav"),
//         new Tone().Player("static/samples/808_snare.wav"),
//         new Tone().Player("static/samples/808_hihat.wav"),
//         new Tone().Player("static/samples/808_tom.wav")
// }
//     var sample = new Audio('static/samples/hihat.wav');
//     sample.load();
//     samples.push(sample);
//     sample = new Audio('static/samples/kick.wav');
//     sample.load();
//     samples.push(sample);
//     sample = new Audio('static/samples/snare.wav');
//     sample.load();
//     samples.push(sample);
//     sample = new Audio('static/samples/tom.wav');
//     sample.load();
//     samples.push(sample);
// }