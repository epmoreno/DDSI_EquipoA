import javax.persistence.*;

@Entity
public class Stock {

    @Id@GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;
    private String nombre;
    private Integer cantidad;

    public Stock() {}
    public Stock(String nombre, Integer cantidad) {
        this.nombre = nombre;
        this.cantidad = cantidad;
    }

    public Long getId() {
        return id;
    }
    public String getNombre() {
        return nombre;
    }
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }
    public Integer getCantidad() {
        return cantidad;
    }
    public void setCantidad(Integer cantidad) {
        this.cantidad = cantidad;
    }
    public void restarCantidad(Integer cantidad){
        this.cantidad -= cantidad;
    }
    
    @Override
    public String toString() {
        return "\n          Stock{" +
                "Id=" + id +
                ", Nombre='" + nombre + '\'' +
                ", Cantidad=" + cantidad +
                '}';
    }
}
