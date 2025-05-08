(function () {
    var project  = app.project;
    var sequence = project.activeSequence;

    if (!sequence) {
        alert("No active sequence found!");
        return;
    }

    // Helper: convert duration in ticks to seconds
    function ticksToSeconds(ticks) {
        return ticks / 254016000000; // Premiere's internal tick rate
    }

    // Helper: recursively find all .mp4 items in the project
    var mp4Items = [];
    function findMP4s(folder) {
        for (var i = 0; i < folder.children.numItems; i++) {
            var item = folder.children[i];
            if (item.type === ProjectItemType.BIN) {
                findMP4s(item);
            } 
            else if (
                item.name &&
                item.name.toLowerCase().slice(-4) === ".mp4"
            ) {
                mp4Items.push(item);
            }
        }
    }
    findMP4s(project.rootItem);

    if (mp4Items.length === 0) {
        alert("No .mp4 files found in the project.");
        return;
    }

    // Shuffle (Fisher–Yates)
    for (var i = mp4Items.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = mp4Items[i];
        mp4Items[i] = mp4Items[j];
        mp4Items[j] = tmp;
    }

    // Insert video‐only on V1
    var videoTrack = sequence.videoTracks[0];
    var timeCursor = 0;
    for (i = 0; i < mp4Items.length; i++) {
    // for (i = 0; i < 40; i++) {
        var clipItem = mp4Items[i];
        var vClip   = videoTrack.insertClip(clipItem, timeCursor);
        var seconds = ticksToSeconds(clipItem.duration);

        // strip any leftover linked audio for this clip
        for (var a = 0; a < sequence.audioTracks.numTracks; a++) {
            var at = sequence.audioTracks[a];
            for (var c = at.clips.numItems - 1; c >= 0; c--) {
                var ac = at.clips[c];
                if (ac.projectItem === clipItem) {
                    if (ac.isLinked()) ac.unlink();
                    ac.remove();
                }
            }
        }

        timeCursor += seconds;
    }

        // ────────────────────────────────────────────────────────────────────────────
    // Mute only Audio-Track 1 (index 0) now that all clips are in
    // ────────────────────────────────────────────────────────────────────────────
    if (sequence.audioTracks.numTracks > 0) {
        // 1 = mute-on, 0 = mute-off
        sequence.audioTracks[0].setMute(1);
    }


    
})();
