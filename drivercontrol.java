class DriverControlModule{

    public static void main(String[] args){
        
        boolean goingToCrash;
        double speed;
        double motorCurrent;
        if(goingToCrash)
            Dont();
        if(speed <= 15)
            GoFaster();
    }
        
    private static void Dont(){
        speed = 0;
        motorCurrent = 0;
        exit;
    }
    
    private static void GoFaster(){
        speed *= 1.5;
    }
}