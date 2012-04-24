(function() {
  var DemoSequence, seq;
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
      this.startTime = new Date().getTime();
      this.running = true;
      this.audio.play();
      return this.step();
    };
    DemoSequence.prototype.stop = function() {
      return this.audio.stop();
    };
    DemoSequence.prototype.step = function() {
      var diff, event;
      if (this.running) {
        window.setTimeout(this.step, 50);
        diff = (new Date().getTime() - this.startTime) / 1000;
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
    seq = new DemoSequence(events);
    if (!seq.running) {
      return seq.play();
    }
    window.seq = seq;
  });
}).call(this);
