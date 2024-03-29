TAU = Math.PI*2

makeRGBA = (triple, alpha) ->
  [r, g, b] = triple
  return "rgba(#{r}, #{g}, #{b}, #{alpha})"

requestAnimFrame = \
  window.requestAnimationFrame || window.mozRequestAnimationFrame || \
  window.webkitRequestAnimationFrame || window.oRequestAnimationFrame || \
  window.msRequestAnimationFrame || (callback) ->
    window.setTimeout(callback, 1000/60)

class Circle
  constructor: (alpha) ->
    dist = Math.random()
    theta = Math.random() * TAU
    @x = dist * Math.cos(theta)
    @y = dist * Math.sin(theta)

    @size = 100 + Math.random() * 200
    @thickness = Math.random() * @size
    @incolor = [120, 120, 140]
    @outcolor = [200, 200, 220]
    @alpha = alpha

    @vx = 0
    @vy = 0

  setColors: (incolor, outcolor) ->
    @incolor = incolor
    @outcolor = outcolor

  tick: () ->
    @y += @vy
    @x += @vx

    @vx -= @x/20000
    @vx *= .999
    @vx += (Math.random() - .5)/4000
    @vy -= @y/15000
    @vy *= .999
    @vy += (Math.random() - .5)/3000

  draw: (ctx) ->
    ctx.fillStyle = makeRGBA(@incolor, @alpha)
    ctx.strokeStyle = makeRGBA(@outcolor, @alpha)
    ctx.lineWidth = @thickness

    screenX = ctx.canvas.width * (@x+0.5)
    screenY = ctx.canvas.height * (@y+0.5)
    @screenX = screenX
    @screenY = screenY
    #console.log(screenX, screenY, @size)
    ctx.beginPath()
    ctx.arc(screenX, screenY, @size/2, 0, TAU)
    ctx.fill()
    ctx.stroke()

class RenderedWord
  constructor: (word, x, y, size, colors) ->
    @word = word
    @x = x
    @y = y
    @colors = colors
    @angle = Math.random() * TAU
    @radius = 1
    @alpha = 0.8
    @vx = 0
    @vy = 0.1
    @ay = Math.random()/200 + 0.01
    @rotationRate = (Math.random() - .5)/40
    @size = size
    @altSize = size
    @fadeRate = 0.99

  tick: () ->
    @y -= @vy
    @radius += @vy

    @x += @vx
    @vx += (Math.random() - .5)/15
    @vy += (Math.random() - .5)/15

    @angle += @rotationRate
    if @angle > TAU
      @angle -= TAU

    @alpha *= @fadeRate
    @size /= Math.sqrt(@fadeRate)
    @altSize /= @fadeRate

  draw: (ctx) ->
    ctx.font = "italic #{@size*1.5}px 'Gentium Basic'"
    ctx.lineWidth = 0
    if @colors.length > 0
      nOthers = Math.min(@colors.length - 1, 3)
      ctx.font = "bold #{@altSize}px 'PT Sans'"
      if nOthers
        for i in [1...nOthers+1]
          ctx.fillStyle = makeRGBA(@colors[i], @alpha*@alpha)
          ctx.fillText(@word, @x + @radius * Math.cos(@angle + TAU*i/nOthers),
                              @y + @radius * Math.sin(@angle + TAU*i/nOthers))
    if @colors.length == 0
      ctx.fillStyle = makeRGBA([255, 255, 255], @alpha)
    else
      ctx.font = "bold #{@size}px 'PT Sans'"
      ctx.fillStyle = makeRGBA(@colors[0], @alpha)
    ctx.fillText(@word, @x, @y)    

class PrettyColors
  constructor: () ->
    @canvas = $('#thecanvas')[0]
    # @canvas.width = window.innerWidth
    # @canvas.height = window.innerHeight
    @ctx = @canvas.getContext "2d"
    @uid = ''+Math.floor(Math.random() * 10000)
    @colors = [[200, 200, 200]]
    @lastText = ''
    @manualTime = 0

    @xPos = 0
    @words = []
    @circles = []
    for i in [0...16]
      @circles.push(new Circle(0.01))
    this.waitForTick()
    @timeout = null

  sendText: (text) ->
    console.log("sent #{text}")
    escapedText = encodeURI(text.replace(/[\/ ]/g, '+'))
    $.ajax
      url: "/input/#{@uid}/#{escapedText}"
      dataType: 'json'
      success: @handleResponse

  waitForTick: =>
    requestAnimFrame(this.tick, @canvas)

  tick: =>
    this.makeBackground()
    for wordObj in @words
      wordObj.draw(@ctx)
      wordObj.tick()
    this.cleanWords()
    this.waitForTick()

  cleanWords: =>
    @words = (w for w in @words when w.alpha > 0.01 and w.y > 0 and w.y < @ctx.canvas.height)
  
  handleResponse: (obj) =>
    console.log('got response')
    if obj.newline
      @xPos = 20
    if obj.weight == 0
      size = 8
    else
      size = 10 + Math.sqrt(obj.weight)
    if obj.weight < 25
      obj.activeColors = obj.activeColors[0...1]
    newWord = new RenderedWord(
    	obj.active,
    	@xPos,
    	@canvas.height/2 + Math.random()*20 - 10,
    	size,
    	obj.activeColors
    )
    this.colors = obj.colors

    @words.push newWord

    @xPos += size*6
    if @xPos + size*6 > @canvas.width
      @xPos += size*6
      @xPos -= @canvas.width

  makeBackground: () ->
    midColor = Math.floor(@colors.length/2)
    @ctx.fillStyle = makeRGBA(@colors[midColor], 0.04)
    @ctx.fillRect(0, 0, @canvas.width, @canvas.height)
    N = @colors.length
    for ci in [0...@circles.length]
      i = ci % N
      j = (ci+1) % N
      @circles[ci].setColors(@colors[i], @colors[j])
      @circles[ci].draw(@ctx)
      @circles[ci].tick()

  triggerText: () =>
    @manualTime = new Date().getTime()

    text = $('#textarea').val()
    text = text.replace(/\n/g, ' ')
    pieces = text.split(" ")
    if (pieces.length > 1)
      word = pieces[0]
      $('#textarea').val(pieces[1...].join(' '))
      if word
        window.colors.sendText(word)
    if pieces.length > 2
      triggerText()

  triggerTextAuto: () =>
    time = new Date().getTime()
    if time - @manualTime > 400
      @manualTime = new Date().getTime()

      text = $('#textarea').val() ? ''
      text = text.replace(/\n/g, ' ')
      pieces = text.split(" ")
      if (pieces.length > 0)
        word = pieces[0]
        $('#textarea').val(pieces[1...].join(' '))
        if word
          window.colors.sendText(word)

$ ->
  window.colors = new PrettyColors()
  console.log("initialized")
  window.setInterval(window.colors.triggerTextAuto, 500)

$('#textarea').keydown ->
  window.colors.triggerText()
$('#textarea').keyup ->
  window.colors.triggerText()

this.PrettyColors = PrettyColors
