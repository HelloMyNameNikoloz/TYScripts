// autocut.jsx
// Splits the active sequence on V1 every 0.5 seconds

(function autocutEveryHalfSecond() {
    var seq = app.project.activeSequence;
    if (!seq) {
        alert("No active sequence open.");
        return;
    }

    // enable the QE DOM
    app.enableQE();
    var qeSeq = qe.project.getActiveSequence();
    if (!qeSeq) {
        alert("Could not get QE sequence.");
        return;
    }

    // untarget all video & audio tracks
    for (var i = 0; i < seq.videoTracks.numTracks; i++) {
        seq.videoTracks[i].setTargeted(false);
    }
    for (var j = 0; j < seq.audioTracks.numTracks; j++) {
        seq.audioTracks[j].setTargeted(false);
    }

    // target only V1
    seq.videoTracks[0].setTargeted(true);

    // grab In/Out points (in seconds)
    var inPoint  = seq.getInPoint().seconds;
    var outPoint = seq.getOutPoint().seconds;

    // *** the only change: use getMenuCommandId, not findMenuCommandId ***
    var addEditCmd = app.getMenuCommandId("Add Edit");
    if (!addEditCmd) {
        alert("Could not find the ‘Add Edit’ menu command.");
        return;
    }

    // loop from In to Out in 0.5-sec steps, cutting at each
    var interval = 0.5;
    for (var t = inPoint + interval; t < outPoint; t += interval) {
        seq.setPlayerPosition(t);
        app.executeCommand(addEditCmd);
    }

    alert("Auto-cut complete: edits every " + interval + " sec on V1.");
})();
