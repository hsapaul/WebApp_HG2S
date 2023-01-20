///////////////////////////////////////////////////
/////////////// DRUM SEQUENCER ////////////////////
///////////////////////////////////////////////////

function stepSequencer(static_url) {
    console.log(static_url);

    document.documentElement.addEventListener('mousedown', () => {
        if (Tone.context.state !== 'running') Tone.context.resume();
    });

// Wait till tone.js is loaded
    setTimeout(function () {

        console.log("tone.js hopefully loaded");

        Tone.setContext(actx);

        // When New Item is detected in Sequencer --> initialize new Tone.js Player
        var sequencer_rows = document.getElementsByClassName("draggables");
        for (var i of sequencer_rows) {
            i.addEventListener("drop", initializeSamples);
        }

        // set tone bpm to 120 initially
        Tone.Transport.bpm.value = 120;

        // var buffer = new Tone.Buffer("{{static_url}}/kicks/BOS_DHT_Kick_One_Shot_Deep_F.wav");

        // Clickable Play/Pause Button
        var start_button = document.getElementById("startSequencerButton");
        start_button.addEventListener("click", startSequencer);

        function startSequencer() {
            if (Tone.Transport.state === "started") {
                // clear the schedule repeat event and set index to 0
                Tone.Transport.clear(Tone.Transport.scheduleRepeat);
                Tone.Transport.position = 0;
                Tone.Transport.stop(0);
                Tone.Transport.cancel();
                set_index_to_zero = true;
                step_counter.innerText = "0";
                for (const $row of $rows) {
                    $row.querySelectorAll('span').forEach($span => $span.classList.remove('bgcolor_avenue'));
                }
            } else {
                initializeSamples();
                // start scheduleRepeat at index 0
                Tone.Transport.start(0);
                Tone.Transport.scheduleRepeat(repeat, "16n", startTime = 0);

            }
        }

        // Initialize drum samples

        const drum_samples = ["", "", "", ""];

        const $rows = document.getElementsByClassName('$row')

        function initializeSamples() {
            console.log("INITIALIZING SAMPLES");
            var alibi_synth = new Tone.Synth().toDestination();
            var select_drum_samples = document.querySelectorAll(".draggables");
            for (var i = 0; i < select_drum_samples.length; i++) {
                // console.log(i, select_drum_samples[i].innerText);
                // if element has button as a child
                if (select_drum_samples[i].querySelector("button")) {
                    var element_name = select_drum_samples[i].innerText;
                    // console.log(i, element_name);
                    if (element_name) {
                        classList = select_drum_samples[i].querySelector("button").classList;
                        category_classes = ["kick_item", "snare_item", "clap_item", "hihat_item", "percussion_item"];
                        for (category in category_classes) {
                            if (classList.contains(category_classes[category])) {
                                var element_category = category_classes[category].slice(0, -5) + "s";
                                var element_url = static_url + element_category + "/" + element_name;
                                console.log("Sequencer Slot:", i);
                                console.log("Element URL:", element_url);
                                drum_samples[i] = new Tone.Player(element_url).toDestination();
                                momentary_volume = document.getElementById("slider_volume_sequencer_" + (i + 1)).value;
                                drum_samples[i].volume.value = Math.round(momentary_volume);
                            }
                        }
                    }
                }
            }
        }

        let index = 0;
        var step_counter = document.getElementById("step-counter");

        let set_index_to_zero = false;

        function repeat(time) {
            // Setzen des Index auf 0 bei Neustart
            if (set_index_to_zero) {index = 0; set_index_to_zero = false;}
            // Modulo 16 damit der Index immer zwischen 0 und 15 bleibt
            let step = index % 16;
            // Anzeige des Steps
            step_counter.innerText = step;
            for (let i = 0; i < $rows.length; i++) {
                let sample = drum_samples[i],
                    $row = $rows[i],
                    $input = $row.querySelector(`span:nth-child(${step + 1}) > input`);
                $row.querySelectorAll('span').forEach($span => $span.classList.remove('bgcolor_avenue'));
                $row.querySelector(`span:nth-child(${step + 1})`).classList.add('bgcolor_avenue');
                if ($input.checked) {
                    try {
                        drum_samples[i].start(time);
                    } catch (e) {
                        drum_samples[i].stop(time);
                        console.log(e);
                        continue;
                    }
                }
            }
            index++;
        }

        // Mixer Sliders
        slider_volume_sequencer = document.getElementsByClassName("slider_volume_sequencer");
        for (let step = 0; step < slider_volume_sequencer.length; step++) {
            slider_volume_sequencer[step].addEventListener("input", function () {
                var volume = this.value;
                if (drum_samples[step]) {
                    drum_samples[step].volume.value = volume;
                } else {
                    console.log("no sample connected on ", step);
                }
            });
        }

        initializeSamples();
    }, 1000);


}