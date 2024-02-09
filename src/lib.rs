use std::collections::HashMap;
use std::process::Command;
use std::os::unix::net::UnixStream;



pub enum Value {
    Integer(i64),
    String(String),
    Float(f64),
    Dictionary(HashMap<String, Value>),
    List(Box<[Value]>),
}

impl Value {
    pub fn to_json(&self) -> String {
        match self {
            Value::Integer(i) => i.to_string(),
            Value::String(s) => s.clone(),
            Value::Float(f) => f.to_string(),
            Value::Dictionary(d) => {
                let mut result = String::from("{");
                for (key, value) in d {
                    result.push_str(&format!("\"{}\": {}, ", key, value.to_json()));
                }
                result.push_str("}");
                result
            }
            Value::List(l) => {
                let mut result = String::from("[");
                for value in l.into_iter() {
                    result.push_str(&format!("{}, ", value.to_json()));
                }
                result.push_str("]");
                result
            }
        }
    }

    pub fn as_json(value: &[Value]) -> String {
        let mut result = String::from("[");
        for v in value {
            result.push_str(&v.to_json());
            result.push_str(", ");
        }
        
        result.push_str("]");
        return result;
    }
}




pub struct ForeignFunction<'a> {
    pub name: &'a str,
}


impl<'a> ForeignFunction<'a> {
    pub fn new<S>(name: &'a S) -> ForeignFunction<'a> 
    where S: AsRef<str> {
    Self {
            name: name.as_ref(),
        }
    }
}

impl ForeignFunction<'_> {
    pub fn call(&self, args: &[Value]) -> Value {
        let mut command = Command::new(self.name);
        for arg in args {
            command.arg(&arg.to_json());
        }
        let json = Value::as_json(args);

        command.env("UFFI_AGS", &json);
        let pid = std::process::id();
        let socket_path = format!("/tmp/uffi_{}", pid);
        command.env("UFFI_SOCKET", &socket_path);
        let handle = command.spawn().unwrap();

        let mut stream = UnixStream::connect(socket_path).unwrap();

    }
}
