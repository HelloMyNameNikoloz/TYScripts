/* scripts-notenZauber/run_audio_then_image.jsx
   Launcher in scripts-notenZauber, runs two scripts that live in the sibling “Scripts” folder.
*/
(function () {
    // 1) Locate this file’s folder (scripts-notenZauber)
    var launcherFile   = new File($.fileName);
    var subFolder      = launcherFile.parent;               // .../scripts-notenZauber
    // 2) Build a reference to the sibling “Scripts” directory
    var parentFolder   = subFolder.parent;                  // …/<project> root
    var scriptsFolder  = new Folder(parentFolder.fsName + "/Scripts");
    if (!scriptsFolder.exists) {
        alert("Cannot find sibling Scripts folder at:\n" + scriptsFolder.fsName);
        return;
    }

    // 3) Define the two scripts in that Scripts folder
    var audioScript = new File(scriptsFolder.fsName + "/insert_random_audios.jsx");
    var imageScript = new File(scriptsFolder.fsName + "/inser_image.jsx");

    // 4) Verify both exist
    if (!audioScript.exists) {
        alert("Missing audio script:\n" + audioScript.fsName);
        return;
    }
    if (!imageScript.exists) {
        alert("Missing image script:\n" + imageScript.fsName);
        return;
    }

    // 5) Run in order
    $.evalFile(audioScript);  // first: random audio placement
    $.evalFile(imageScript);  // second: image stretch & scale

    
})();
