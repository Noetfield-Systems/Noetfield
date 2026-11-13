/** Noetfield Connect participant gateway. Validated same-origin forwarding, no public operator key. */
module.exports = async function handler(req,res) {
  res.setHeader("Cache-Control","private, no-store");
  res.setHeader("Referrer-Policy","no-referrer");
  res.setHeader("X-Content-Type-Options","nosniff");
  if(req.method!=="POST")return res.status(405).json({detail:"METHOD_NOT_ALLOWED"});
  const origin=req.headers.origin;
  if(origin){
    try{if(new URL(origin).host!==req.headers.host)return res.status(403).json({detail:"ORIGIN_REJECTED"});}
    catch{return res.status(403).json({detail:"ORIGIN_REJECTED"});}
  }
  const body=req.body;
  if(!body || typeof body!=="object" || Array.isArray(body))return res.status(400).json({detail:"INVALID_BODY"});
  const allowed=["request_id","email"];
  if(Object.keys(body).some(k=>!allowed.includes(k)))return res.status(422).json({detail:"INVALID_FIELDS"});
  if(typeof body.request_id!=="string"||!/^RID-CNX-[A-Za-z0-9_-]{12,}$/.test(body.request_id)||
     body.request_id.length>64 || typeof body.email!=="string"||body.email.length>254||
     !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(body.email))return res.status(422).json({detail:"INVALID_REFERENCE"});
  
  const base=(process.env.PLATFORM_API_BASE||"https://platform.noetfield.com").replace(/\/$/,"");
  try{
    const upstream=await fetch(base+"/api/connect/participant/status",{
      method:"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},
      body:JSON.stringify(body),signal:AbortSignal.timeout(12000),redirect:"error",
    });
    const data=await upstream.json().catch(()=>({}));
    if(!upstream.ok)return res.status([400,403,404,409,422,429,503].includes(upstream.status)?upstream.status:502)
      .json({detail:typeof data.detail==="string"?data.detail:"UPSTREAM_UNAVAILABLE"});
    return res.status(200).json({
      found:data.found===true,intake_id:String(data.intake_id||""),
      stage:String(data.stage||"NEW"),detail:String(data.detail||""),
      created_at:data.created_at||null,updated_at:data.updated_at||null,
      independently_verified:false,receipt_type:"SOURCE_BACKED_PARTICIPANT_STATUS"
    });
  }catch{return res.status(503).json({detail:"PLATFORM_UNAVAILABLE"});}
};
