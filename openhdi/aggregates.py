from bson.code import Code
from mongo import get_db 

MAP_CTCU = Code("""function() {
    var user_id = this.user_id; 
    this.weightings.forEach(function(w) {
        w.items.forEach(function(i) {
            var indicator = i[0];
            var weight = i[1];
            
            var data = db.datum.find({'indicator_id': indicator});
            data.forEach(function(datum) {
                var value = (weight/100) * datum.value;
                emit({category: w.category, time: datum.time, 
                      country: datum.country, user_id: user_id},
                     value);
                emit({category: w.category, time: datum.time, 
                      country: datum.country, user_id: '__sum__'},
                     value);
            }); 
        }); 
    }); 
}""")

REDUCE_CTCU = Code("""function(key, values) {
    var sum = 0; 
    values.forEach(function(v) { sum += v; });
    db.aggregates.update({"category" : key.category, 
                          "time" : key.time, 
                          "country" : key.country, 
                          "user_id" : key.user_id},
                          {'$set': {'value': sum}}, upsert=true); 
    return sum/values.length;
}""")


MAP_TCU = Code("""function() {
    emit({time: this.time, country: this.country, user_id: this.user_id},
         {category: this.category, value: this.value})
}""")

REDUCE_TCU = Code("""function(key, values) {
    var meta_f = 0; 
    values.forEach(function(m) {
        if (m.category == 'meta') meta_f = m.value; 
    }); 
    
    var aggregate = 0; 
    values.forEach(function(c) {
        if (c.category != 'meta')
            aggregate += (meta_f * c.value);
    }); 
    value = aggregate/(values.length-1); 
    db.aggregates.update({"category": '__sum__', 
                          "time" : key.time, 
                          "country" : key.country, 
                          "user_id" : key.user_id},
                         {'$set': {'value': value}}, upsert=true);
    return value;
}""")

def compute(): 
    from time import time 
    db = get_db()
    t0 = time() 
    db.aggregates.remove()
    db.user.map_reduce(MAP_CTCU, REDUCE_CTCU)
    t1 = time() 
    print "CTCU", t1-t0
    db.aggregates.map_reduce(MAP_TCU, REDUCE_TCU)
    t2 = time()
    print "TCU", t2-t1
    print "TOTAL", t2-t0

if __name__ == '__main__':
    compute() 
