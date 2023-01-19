///////////////////////////////////////////////////
///////////////// PIANO ROLL //////////////////////
///////////////////////////////////////////////////

function pianoRoll() {

    const fluidr3_path = "/static/music_gallery/json_soundfonts/fluidR3.json";

    // read the fluidr3 soundfont names and place them in a select dropdown
    fetch(fluidr3_path)
        .then(response => response.json())
        .then(data => {
            const soundfont_select = document.getElementById("soundfont_select");
            for (let i = 0; i < data.length; i++) {
                const option = document.createElement("option");
                option.value = data[i];
                option.text = data[i];
                soundfont_select.appendChild(option);
            }
        })
        .catch(error => console.log(error));

    osc_types = ["sine", "square", "sawtooth", "triangle"];

    setTimeout(function () {

        timebase = 480;
        // actx2 = new AudioContext();
        let instrument;
        initializeSoundfont("accordion");

        var play_button = document.getElementById("startSequencerButton");
        play_button.addEventListener("click", function () {
            console.log("play function (playground_pianoRoll.js)");
            // actx.resume();
            document.getElementById("pianoroll").play(actx, Callback_sf);
        });

        var soundfont_select = document.getElementById("soundfont_select");
        soundfont_select.addEventListener("change", function () {
            console.log("soundfont_select");
            new_sf_name = soundfont_select.value;
            console.log(soundfont_select.value);
            initializeSoundfont(new_sf_name);
        });

        // Called at loading page and if soundfont change detected
        function initializeSoundfont(sf_name) {
            instrument = Soundfont.instrument(actx, sf_name).then(function (instr) {
                instrument = instr;
                console.log("instrument loaded");
                // make play button visible
                // play_button.style.display = "inline-block";
                document.getElementById('invisible').style.display = "block";
            });
        }


        function Callback_sf(ev) {
            console.log("play: " + ev.n);
            var ev_time = ev.t;
            var ev_gain = ev.g;
            var ev_note = ev.n;
            const start = Date.now();
            // play instrument now
            // only play for the duration of the note


            try {
                instrument.play(ev_note, ev_time, {gain: 0.5});
            } catch (e) {
                console.log(e);
            }
            // console.log("instrument.play took " + (Date.now() - start) + " ms");
        }

        function Callback_osc(ev) {
            // event: {t: 0.442, g: 0.5, n: 73} --> t: time, g: gain, n: note
            console.log("play now: " + ev.n);
            // instrument.play(ev.n, actx.currentTime, 0.5);
            var o = actx.createOscillator();
            var g = actx.createGain();
            // Get selected osc type
            var osc_type = osc_types[document.getElementById("osc_type").selectedIndex];
            o.type = osc_type;
            o.detune.value = (ev.n - 69) * 100;
            g.gain.value = 0;
            o.start(actx.currentTime);
            g.gain.setTargetAtTime(0.2, ev.t, 0.005);
            g.gain.setTargetAtTime(0, ev.g, 0.1);
            o.connect(g);
            g.connect(actx.destination);
        }
    }, 500);

}