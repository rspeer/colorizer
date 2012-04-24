(function() {
  var DemoSequence;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  DemoSequence = (function() {
    function DemoSequence(events) {
      this.step = __bind(this.step, this);
      this.stop = __bind(this.stop, this);
      this.play = __bind(this.play, this);      this.eventList = events;
      this.listPos = 0;
      this.running = false;
      this.audio = $('#theaudio')[0];
    }
    DemoSequence.prototype.play = function() {
      this.listPos = 0;
      this.running = true;
      this.audio.seek(0);
      this.audio.play();
      return this.step();
    };
    DemoSequence.prototype.stop = function() {
      return this.audio.pause();
    };
    DemoSequence.prototype.step = function() {
      var diff, event;
      if (this.running) {
        window.setTimeout(this.step, 50);
        diff = this.audio.currentTime;
        event = this.eventList[this.listPos];
        if (diff > event.time) {
          window.colors.handleResponse(event);
          return this.listPos += 1;
        }
      }
    };
    return DemoSequence;
  })();
  $(function() {
    var seq;
    seq = new DemoSequence(events);
    if (!seq.running) {
      seq.play();
    }
    return window.seq = seq;
  });
}).call(this);
