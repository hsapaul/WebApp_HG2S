function configure_mode_appearance(bool) {
    // Switches
    var textColor = !bool ? "color_white" : "color_black";
    var bgColor = !bool ? "bgcolor_black" : "bgcolor_white";
    var bgColor_secondary = !bool ? "bgcolor_darkgrey" : "bgcolor_lightgrey";
    var remove_secondary = !bool ? "bgcolor_lightgrey" : "bgcolor_darkgrey";


    // Change Body BG Color
    var pageContent = document.getElementsByClassName("page-content")[0];
    pageContent.classList.add(bgColor);
    pageContent.classList.remove("bg" + textColor);
    var contrast_appearance = document.querySelectorAll(".contrast-appearance");

    // Change paragraph and all headings text color
    pageContent.querySelectorAll("p, h1, h2, h3, h4, h5, h6, label, button, li").forEach(function (el) {
        el.classList.add(textColor);
        el.classList.remove(bgColor.replace("bg", ""));
    });

    pageContent.querySelectorAll("a").forEach(function (el) {
        if (textColor == "color_white") {
            el.classList.add("a_dark"); el.classList.remove("a_light");
        } else {
            el.classList.add("a_light"); el.classList.remove("a_dark");
        }
    });

    // Change the contrasted areas
    for (var i = 0; i < contrast_appearance.length; i++) {
        contrast_appearance[i].classList.add(remove_secondary);
        contrast_appearance[i].classList.remove(bgColor);
        contrast_appearance[i].querySelectorAll("p, h1, h2, h3, h4, h5, h6, label, button, li, a").forEach(function (el) {
            el.classList.add(bgColor.replace("bg", ""));
            el.classList.remove(textColor);
        });
    }


    // Change Card BG color
    document.querySelectorAll(".card").forEach(function (card) {
        card.classList.add(bgColor_secondary);
        card.classList.remove(remove_secondary);
    });


    // Button Colors
    document.querySelectorAll(".main-btn").forEach(function (btn) {
        // const bootstrap_btn_outline = !bool ? "btn-outline-light" : "btn-outline-dark";
        // const bootstrap_opposite = !bool ? "btn-outline-dark" : "btn-outline-light";
        // btn.classList.add(bootstrap_btn_outline);
        // btn.classList.remove(bootstrap_opposite);
    });


}

function configure_theme_appearance(theme) {

    var seperators = document.querySelectorAll(".seperator-line")

    if (theme == "HG2S Original") {
        document.body.classList.remove("bgcolor_purple", "bgcolor_avenue");
        document.body.classList.add('bgcolor_original');
        seperators.forEach(function (el) {
            el.classList.remove("bdcolor_purple", "bdcolor_avenue");
            el.classList.add("bdcolor_original");
        });
    } else if (theme == "Purple Darkness") {
        document.body.classList.remove("bgcolor_original", "bgcolor_avenue");
        document.body.classList.add('bgcolor_purple');
        seperators.forEach(function (el) {
            el.classList.remove("bdcolor_original", "bdcolor_avenue");
            el.classList.add("bdcolor_purple");
        });
    } else if (theme == "Sunlight Avenue") {
        document.body.classList.remove("bgcolor_original", "bgcolor_purple");
        document.body.classList.add('bgcolor_avenue');
        seperators.forEach(function (el) {
            el.classList.remove("bdcolor_original", "bdcolor_purple");
            el.classList.add("bdcolor_avenue");
        });
    }

}