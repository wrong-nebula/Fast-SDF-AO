async s => {
  const d = window.aoDemo;
  d.renderer.setAnimationLoop(null);
  await d.setScene('archive');
  d.setQuality('high');
  d.setGI(true);
  d.setMultiBounceGI(false);
  d.setDynamicAO(true);
  d.select(64);
  d.setForceMesh(false);
  const plank = d.movers.find(m => m.name === 'plank');
  plank.geometry.scale(1, 1, s.plank_half[2] / .08);
  plank.analyticParam.z = s.plank_half[2];
  plank.pose = i => ({x:s.start_x + i*s.step_x, y:s.center_y, z:s.center_z, rz:Math.PI/2});
  d.movers.filter(m => m !== plank).forEach((m,i) => {
    m.pose = () => ({x:100+i*3, y:100, z:1});
    m.object.visible = false;
  });
  const gl = d.renderer.getContext(), tiny = new Uint8Array(4);
  function camera(position) {
    d.camera.position.fromArray(position);
    d.camera.lookAt(...s.target);
    d.camera.updateMatrixWorld();
  }
  function reset() { d.traced.frame.value=0; d.resetHistory(); }
  function sync() { gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,tiny); gl.finish(); }
  window.start = mask => { d.setMask(mask); d.setGIMask(false); camera(s.pre_camera); reset(); };
  window.draw = ([i,mode]) => {
    if (i === 1 || mode === 'reference') camera(s.post_camera);
    d.updateMovers(Math.max(0,i));
    if (i === 1 || mode === 'reference') reset();
    if (mode === 'time') sync();
    const t = performance.now();
    for(let k=0;k<(mode==='reference'?96:1);k++) d.render(64);
    if (mode==='time') {sync(); return performance.now()-t;}
    if (mode==='discard') return null;
    return d.renderer.domElement.toDataURL('image/png').split(',')[1];
  };
  return gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_RENDERER_WEBGL);
}
