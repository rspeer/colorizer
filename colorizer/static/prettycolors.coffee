TAU = Math.PI*2

makeRGBA = (triple, alpha) ->
  [r, g, b] = triple
  return "rgba(#{r}, #{g}, #{b}, #{alpha})"

requestAnimFrame = \
  window.requestAnimationFrame || window.mozRequestAnimationFrame || \
  window.webkitRequestAnimationFrame || window.oRequestAnimationFrame || \
  window.msRequestAnimationFrame || (callback) ->
    window.setTimeout(callback, 1000/60)

class RenderedWord
  constructor: (word, x, y, size, colors) ->
    @word = word
    @x = x
    @y = y
    @colors = colors
    @angle = Math.random() * TAU
    @radius = 2
    @alpha = 1
    @vx = 0
    @vy = 0
    @ay = Math.random()/200 + 0.01
    @rotationRate = (Math.random() - .5)/40
    @size = size
    @altSize = size
    @fadeRate = 0.995

  tick: () ->
    @y -= @vy
    @radius += @vy
    @vy += @ay

    @x += @vx
    @vx += (Math.random() - .5)/10 

    @angle += @rotationRate
    if @angle > TAU
      @angle -= TAU

    @alpha *= @fadeRate
    @size /= @fadeRate
    @altSize /= @fadeRate*@fadeRate

  draw: (ctx) ->
    ctx.font = "italic #{@size*1.5}px 'Gentium Basic'"
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
    @canvas.width = window.innerWidth
    @canvas.height = window.innerHeight
    @ctx = @canvas.getContext "2d"
    @uid = ''+Math.floor(Math.random() * 10000)
    @colors = [[200, 200, 200]]
    @lastText = ''

    @xPos = 0
    @words = []
    this.waitForTick()

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
    @words = (w for w in @words when w.alpha > 0.2 and w.y > 0)
  
  handleResponse: (obj) =>
    console.log('got response')
    size = 12 + Math.sqrt(obj.weight)
    if obj.weight == 0
      size = 12
    else
      size = 20 + Math.sqrt(obj.weight)*2
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
    N = @colors.length
    for i in [0...@colors.length]
      w = @canvas.width
      @ctx.fillStyle = makeRGBA(@colors[i], 1)
      @ctx.fillRect(i*w/N, 0, w/N, @canvas.height)

$ ->
  window.colors = new PrettyColors()
  console.log("initialized")

$('#textarea').keyup ->
  text = $('#textarea').val()
  if text != colors.lastText
    colors.lastText = text
    lastChar = text.substring(text.length-1)
    if lastChar == " " or lastChar == "\n"
      words = text.substring(0, text.length-1).split(' ')
      endWords = words[words.length-1]
      if endWords?
        window.colors.sendText(endWords)

this.PrettyColors = PrettyColors
