/* scripts-notenZauber/run_video_then_audio.jsx
   Launcher in scripts-notenZauber, runs two scripts that live in the sibling “Scripts” folder:
   1) insert_random_mp4_video_only.jsx
   2) insert_random_audios.jsx
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
    var videoScript   = new File(scriptsFolder.fsName + "/insert_random_mp4_video_only.jsx");
    var audioScript   = new File(scriptsFolder.fsName + "/insert_random_audios.jsx");

    // 4) Verify both exist
    if (!videoScript.exists) {
        alert("Missing video script:\n" + videoScript.fsName);
        return;
    }
    if (!audioScript.exists) {
        alert("Missing audio script:\n" + audioScript.fsName);
        return;
    }

    // 5) Run in order
    $.evalFile(videoScript);  // first: random video placement
    $.evalFile(audioScript);  // second: random audio placement

    
})();
