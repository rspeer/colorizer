(function() {
  var Circle, PrettyColors, RenderedWord, TAU, makeRGBA, requestAnimFrame;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  TAU = Math.PI * 2;
  makeRGBA = function(triple, alpha) {
    var b, g, r;
    r = triple[0], g = triple[1], b = triple[2];
    return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")";
  };
  requestAnimFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function(callback) {
    return window.setTimeout(callback, 1000 / 60);
  };
  Circle = (function() {
    function Circle(alpha) {
      var dist, theta;
      dist = Math.random();
      theta = Math.random() * TAU;
      this.x = dist * Math.cos(theta);
      this.y = dist * Math.sin(theta);
      this.size = 100 + Math.random() * 200;
      this.thickness = Math.random() * this.size;
      this.incolor = [120, 120, 140];
      this.outcolor = [200, 200, 220];
      this.alpha = alpha;
      this.vx = 0;
      this.vy = 0;
    }
    Circle.prototype.setColors = function(incolor, outcolor) {
      this.incolor = incolor;
      return this.outcolor = outcolor;
    };
    Circle.prototype.tick = function() {
      this.y += this.vy;
      this.x += this.vx;
      this.vx -= this.x / 20000;
      this.vx *= .999;
      this.vx += (Math.random() - .5) / 4000;
      this.vy -= this.y / 15000;
      this.vy *= .999;
      return this.vy += (Math.random() - .5) / 3000;
    };
    Circle.prototype.draw = function(ctx) {
      var screenX, screenY;
      ctx.fillStyle = makeRGBA(this.incolor, this.alpha);
      ctx.strokeStyle = makeRGBA(this.outcolor, this.alpha);
      ctx.lineWidth = this.thickness;
      screenX = ctx.canvas.width * (this.x + 0.5);
      screenY = ctx.canvas.height * (this.y + 0.5);
      this.screenX = screenX;
      this.screenY = screenY;
      ctx.beginPath();
      ctx.arc(screenX, screenY, this.size / 2, 0, TAU);
      ctx.fill();
      return ctx.stroke();
    };
    return Circle;
  })();
  RenderedWord = (function() {
    function RenderedWord(word, x, y, size, colors) {
      this.word = word;
      this.x = x;
      this.y = y;
      this.colors = colors;
      this.angle = Math.random() * TAU;
      this.radius = 1;
      this.alpha = 0.8;
      this.vx = 0;
      this.vy = 0.1;
      this.ay = Math.random() / 200 + 0.01;
      this.rotationRate = (Math.random() - .5) / 40;
      this.size = size;
      this.altSize = size;
      this.fadeRate = 0.99;
    }
    RenderedWord.prototype.tick = function() {
      this.y -= this.vy;
      this.radius += this.vy;
      this.x += this.vx;
      this.vx += (Math.random() - .5) / 15;
      this.vy += (Math.random() - .5) / 15;
      this.angle += this.rotationRate;
      if (this.angle > TAU) {
        this.angle -= TAU;
      }
      this.alpha *= this.fadeRate;
      this.size /= Math.sqrt(this.fadeRate);
      return this.altSize /= this.fadeRate;
    };
    RenderedWord.prototype.draw = function(ctx) {
      var i, nOthers, _ref;
      ctx.font = "italic " + (this.size * 1.5) + "px 'Gentium Basic'";
      ctx.lineWidth = 0;
      if (this.colors.length > 0) {
        nOthers = Math.min(this.colors.length - 1, 3);
        ctx.font = "bold " + this.altSize + "px 'PT Sans'";
        if (nOthers) {
          for (i = 1, _ref = nOthers + 1; 1 <= _ref ? i < _ref : i > _ref; 1 <= _ref ? i++ : i--) {
            ctx.fillStyle = makeRGBA(this.colors[i], this.alpha * this.alpha);
            ctx.fillText(this.word, this.x + this.radius * Math.cos(this.angle + TAU * i / nOthers), this.y + this.radius * Math.sin(this.angle + TAU * i / nOthers));
          }
        }
      }
      if (this.colors.length === 0) {
        ctx.fillStyle = makeRGBA([255, 255, 255], this.alpha);
      } else {
        ctx.font = "bold " + this.size + "px 'PT Sans'";
        ctx.fillStyle = makeRGBA(this.colors[0], this.alpha);
      }
      return ctx.fillText(this.word, this.x, this.y);
    };
    return RenderedWord;
  })();
  PrettyColors = (function() {
    function PrettyColors() {
      this.triggerTextAuto = __bind(this.triggerTextAuto, this);
      this.triggerText = __bind(this.triggerText, this);
      this.handleResponse = __bind(this.handleResponse, this);
      this.cleanWords = __bind(this.cleanWords, this);
      this.tick = __bind(this.tick, this);
      this.waitForTick = __bind(this.waitForTick, this);
      var i;
      this.canvas = $('#thecanvas')[0];
      this.ctx = this.canvas.getContext("2d");
      this.uid = '' + Math.floor(Math.random() * 10000);
      this.colors = [[200, 200, 200]];
      this.lastText = '';
      this.manualTime = 0;
      this.xPos = 0;
      this.words = [];
      this.circles = [];
      for (i = 0; i < 16; i++) {
        this.circles.push(new Circle(0.01));
      }
      this.waitForTick();
      this.timeout = null;
    }
    PrettyColors.prototype.sendText = function(text) {
      var escapedText;
      console.log("sent " + text);
      escapedText = encodeURI(text.replace(/[\/ ]/g, '+'));
      return $.ajax({
        url: "/input/" + this.uid + "/" + escapedText,
        dataType: 'json',
        success: this.handleResponse
      });
    };
    PrettyColors.prototype.waitForTick = function() {
      return requestAnimFrame(this.tick, this.canvas);
    };
    PrettyColors.prototype.tick = function() {
      var wordObj, _i, _len, _ref;
      this.makeBackground();
      _ref = this.words;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        wordObj = _ref[_i];
        wordObj.draw(this.ctx);
        wordObj.tick();
      }
      this.cleanWords();
      return this.waitForTick();
    };
    PrettyColors.prototype.cleanWords = function() {
      var w;
      return this.words = (function() {
        var _i, _len, _ref, _results;
        _ref = this.words;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          w = _ref[_i];
          if (w.alpha > 0.01 && w.y > 0 && w.y < this.ctx.canvas.height) {
            _results.push(w);
          }
        }
        return _results;
      }).call(this);
    };
    PrettyColors.prototype.handleResponse = function(obj) {
      var newWord, size;
      console.log('got response');
      if (obj.newline) {
        this.xPos = 20;
      }
      if (obj.weight === 0) {
        size = 8;
      } else {
        size = 10 + Math.sqrt(obj.weight);
      }
      if (obj.weight < 25) {
        obj.activeColors = obj.activeColors.slice(0, 1);
      }
      newWord = new RenderedWord(obj.active, this.xPos, this.canvas.height / 2 + Math.random() * 20 - 10, size, obj.activeColors);
      this.colors = obj.colors;
      this.words.push(newWord);
      this.xPos += size * 6;
      if (this.xPos + size * 6 > this.canvas.width) {
        this.xPos += size * 6;
        return this.xPos -= this.canvas.width;
      }
    };
    PrettyColors.prototype.makeBackground = function() {
      var N, ci, i, j, midColor, _ref, _results;
      midColor = Math.floor(this.colors.length / 2);
      this.ctx.fillStyle = makeRGBA(this.colors[midColor], 0.04);
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      N = this.colors.length;
      _results = [];
      for (ci = 0, _ref = this.circles.length; 0 <= _ref ? ci < _ref : ci > _ref; 0 <= _ref ? ci++ : ci--) {
        i = ci % N;
        j = (ci + 1) % N;
        this.circles[ci].setColors(this.colors[i], this.colors[j]);
        this.circles[ci].draw(this.ctx);
        _results.push(this.circles[ci].tick());
      }
      return _results;
    };
    PrettyColors.prototype.triggerText = function() {
      var pieces, text, word;
      this.manualTime = new Date().getTime();
      text = $('#textarea').val();
      text = text.replace(/\n/g, ' ');
      pieces = text.split(" ");
      if (pieces.length > 1) {
        word = pieces[0];
        $('#textarea').val(pieces.slice(1).join(' '));
        if (word) {
          window.colors.sendText(word);
        }
      }
      if (pieces.length > 2) {
        return triggerText();
      }
    };
    PrettyColors.prototype.triggerTextAuto = function() {
      var pieces, text, time, word;
      time = new Date().getTime();
      if (time - this.manualTime > 400) {
        this.manualTime = new Date().getTime();
        text = $('#textarea').val();
        text = text.replace(/\n/g, ' ');
        pieces = text.split(" ");
        if (pieces.length > 0) {
          word = pieces[0];
          $('#textarea').val(pieces.slice(1).join(' '));
          if (word) {
            return window.colors.sendText(word);
          }
        }
      }
    };
    return PrettyColors;
  })();
  $(function() {
    window.colors = new PrettyColors();
    console.log("initialized");
    return window.setInterval(window.colors.triggerTextAuto, 500);
  });
  $('#textarea').keydown(function() {
    return window.colors.triggerText();
  });
  $('#textarea').keyup(function() {
    return window.colors.triggerText();
  });
  this.PrettyColors = PrettyColors;
}).call(this);
