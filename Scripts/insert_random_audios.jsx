(function () {
    var project  = app.project;
    var sequence = project.activeSequence;

    if (!sequence) {
        alert("No active sequence found.");
        return;
    }

    // ────────────────────────────────────────────────────────────────────────────
    // constants & helpers
    // ────────────────────────────────────────────────────────────────────────────
    var AUDIO_BIN_NAME = "audios";
    var audioItems     = [];

    function ticksToSeconds(ticks) {
        return ticks / 254016000000;        // Premiere’s internal tick-rate
    }

    // find a bin by (exact) name anywhere in the project
    function findBinByName(parentItem, name) {
        for (var i = 0; i < parentItem.children.numItems; i++) {
            var child = parentItem.children[i];
            if (child.type === ProjectItemType.BIN) {
                if (child.name === name) { return child; }
                var nested = findBinByName(child, name);
                if (nested) { return nested; }
            }
        }
        return null;
    }

    // collect all .mp3 or .wav items in that bin (non-recursive)
    function findAudioItems(bin) {
        for (var i = 0; i < bin.children.numItems; i++) {
            var item = bin.children[i];
            if (item.type === ProjectItemType.CLIP &&
                item.name &&
                (item.name.toLowerCase().slice(-4) === ".mp3" ||
                 item.name.toLowerCase().slice(-4) === ".wav")) {
                audioItems.push(item);
            }
        }
    }

    // ────────────────────────────────────────────────────────────────────────────
    // gather audio clips from the “audios” bin
    // ────────────────────────────────────────────────────────────────────────────
    var audioBin = findBinByName(project.rootItem, AUDIO_BIN_NAME);

    if (!audioBin)          { alert("❌ No bin named 'audios' found."); return; }
    findAudioItems(audioBin);
    if (!audioItems.length) { alert("❌ No .mp3 or .wav items in the 'audios' bin."); return; }

    // shuffle (Fisher-Yates)
    for (var i = audioItems.length - 1; i > 0; i--) {
        var j   = Math.floor(Math.random() * (i + 1));
        var tmp = audioItems[i];
        audioItems[i] = audioItems[j];
        audioItems[j] = tmp;
    }

    // ────────────────────────────────────────────────────────────────────────────
    // make sure an A2 track exists, then insert every clip back-to-back
    // ────────────────────────────────────────────────────────────────────────────
    // ensure there are at least 2 audio tracks
    if (sequence.audioTracks.numTracks < 2) {
        // add however many are missing to get to index 1
        var needed = 2 - sequence.audioTracks.numTracks;
        sequence.audioTracks.addTracks(needed);
    }

    var audioTrack = sequence.audioTracks[1];   // A2
    var timeCursor = 0.0;

    for (i = 0; i < audioItems.length; i++) {
        var clipItem = audioItems[i];
        audioTrack.insertClip(clipItem, timeCursor);
        timeCursor += ticksToSeconds(clipItem.duration);
    }

    
})();
