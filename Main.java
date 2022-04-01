class Main {
  public static void main(String[] args) {
    Animal g1 = new Giraffe();
    Animal g2 = new Giraffe("Lily", 1, "female", 2011.2, 7.5, 62);
    System.out.println(g1);
    System.out.println("--------------");
    System.out.println(g2);
    System.out.println("--------------");
    System.out.print("Lily says: ");
    g2.eat();
  }
}
