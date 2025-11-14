//^
//^ HEAD
//^

//> HEAD -> CROSS-SCOPE TRAIT
use crate::runtime::Value;


//^
//^ UNDEFINED
//^

//> UNDEFINED -> STRUCT
#[derive(Clone)]
pub struct _Undefined {}

//> UNDEFINED -> IMPLEMENTATION
impl crate::runtime::Id for _Undefined {const ID: &'static str = "_Undefined";} 
impl crate::runtime::Value for _Undefined {
    fn id(&self) -> &'static str {"_Undefined"}
    fn ctrlcv(&self) -> crate::Box<dyn crate::runtime::Value> {return crate::Box::new(self.clone())}
    fn locale(&self, code: u8) -> () {match code {
        _ => {crate::stdout::crash(crate::stdout::Code::LocaleNotFound)}
    }}
} impl _Undefined {}