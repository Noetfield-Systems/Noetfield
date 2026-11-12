/** Same-origin, bearer-authorized participant response proxy to canonical Platform. */
module.exports = async function handler(req,res) {
  res.setHeader("Cache-Control","no-store, private");
  res.setHeader("Referrer-Policy","no-referrer");
  res.setHeader("X-Content-Type-Options","nosniff");
  if(req.method!=="POST")return res.status(405).json({detail:"METHOD_NOT_ALLOWED"});
  const body=req.body||{};
  if(!body||typeof body!=="object"||Array.isArray(body))return res.status(400).json({detail:"INVALID_BODY"});
  const fields=["intake_id","invitation_id","token","email","decision"];
  if(Object.keys(body).some(k=>!fields.includes(k))||fields.some(k=>typeof body[k]!=="string"))
    return res.status(422).json({detail:"INVALID_RESPONSE_FIELDS"});
  if(!/^INT-[A-Za-z0-9-]{6,80}$/.test(body.intake_id)||!/^inv_[0-9a-f]{16}$/.test(body.invitation_id)||
      body.token.length<32||body.token.length>200||body.email.length>254||
      !["accept","decline"].includes(body.decision))
    return res.status(422).json({detail:"INVALID_INVITATION"});
  const origin=(process.env.PLATFORM_API_BASE||"https://platform.noetfield.com").replace(/\/$/,"");
  try{
    const upstream=await fetch(origin+"/api/opportunities/invitations/respond",{
      method:"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},
      body:JSON.stringify(body),redirect:"error",
    });
    const json=await upstream.json().catch(()=>({}));
    if(!upstream.ok)return res.status([403,404,409,410,422,503].includes(upstream.status)?upstream.status:502)
      .json({detail:typeof json.detail==="string"?json.detail:"UPSTREAM_REJECTED"});
    return res.status(200).json({
      received:json.received===true, state:String(json.state||""),
      receipt_type:"SOURCE_STORED_TOKEN_HOLDER_RESPONSE",
      mailbox_ownership_verified:false, external_action_executed:false,
    });
  }catch(_err){return res.status(503).json({detail:"PLATFORM_UNAVAILABLE"});}
};
