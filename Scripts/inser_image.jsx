(function () {
    var proj = app.project,
        seq  = proj.activeSequence;
    if (!seq) { alert("No active sequence!"); return; }

    /* 1️⃣  Find first audio track that has clips (A2 in your case) */
    var aTrack = null;
    for (var t = 0; t < seq.audioTracks.numTracks; t++) {
        if (seq.audioTracks[t].clips.numItems > 0) { aTrack = seq.audioTracks[t]; break; }
    }
    if (!aTrack) { alert("No audio clips in any track."); return; }

    /* 2️⃣  Get earliest start and latest end *Time objects* (not numbers) */
    var first = aTrack.clips[0];
    var audioStart = first.start;     // Time object
    var audioEnd   = first.end;       // Time object

    for (var i = 1; i < aTrack.clips.numItems; i++) {
        var c = aTrack.clips[i];
        if (c.start.ticks < audioStart.ticks) audioStart = c.start;
        if (c.end.ticks   > audioEnd.ticks)   audioEnd   = c.end;
    }

    /* 3️⃣  Grab first item in the “images” bin */
    function findBin(folder, name) {
        for (var j = 0; j < folder.children.numItems; j++) {
            var it = folder.children[j];
            if (it.type === ProjectItemType.BIN) {
                if (it.name === name) return it;
                var nested = findBin(it, name);
                if (nested) return nested;
            }
        }
        return null;
    }
    var imgBin = findBin(proj.rootItem, "images");
    if (!imgBin || imgBin.children.numItems === 0) {
        alert("No media in a bin named “images”.");
        return;
    }
    var imgItem = imgBin.children[0];

    /* 4️⃣  Ensure V1 exists, insert the still at audioStart */
    if (seq.videoTracks.numTracks < 1) seq.videoTracks.addTracks(1);
    var V1 = seq.videoTracks[0];
    V1.insertClip(imgItem, audioStart.ticks);             // insert at start (ticks)

    /* the new TrackItem is always the last one in V1.clips */
    var clip = V1.clips[V1.clips.numItems - 1];

    /* 5️⃣  Stretch: simply assign end to audioEnd (both are Time objs) */
    clip.end = audioEnd;

    /* 6️⃣  Scale Motion → Scale = 127 % */
    for (var ci = 0; ci < clip.components.numItems; ci++) {
        var comp = clip.components[ci];
        if (comp.matchName === "ADBE Motion" || comp.displayName === "Motion") {
            for (var pi = 0; pi < comp.properties.numItems; pi++) {
                var prop = comp.properties[pi];
                if (prop.displayName === "Scale") {
                    prop.setValue(127, true);
                    break;
                }
            }
            break;
        }
    }

    
})();
