import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import javax.persistence.*;

@Entity
public class Pedido {
    
    @Id@GeneratedValue(strategy = GenerationType.IDENTITY) private Long id;
    @ManyToOne private Persona cliente;
    @ElementCollection private Map<Stock, Integer> detallesPedido = new HashMap<>();
    private Date fecha;

    public Pedido() {}
    public Pedido( Persona cliente){
        this.cliente = cliente;
        this.fecha = new Date(System.currentTimeMillis());
    }

    public Long getId(){
        return id;
    }
    public Persona getPersona(){
        return cliente;
    }
    public Map<Stock, Integer> getDetallesPedido(){
        return detallesPedido;
    }
    public Date getFecha(){
        return fecha;
    }
    public void setPersona(Persona cliente){
        this.cliente = cliente;
    }
    public void setDetallesPedido(Map<Stock, Integer> detallesPedido){
        this.detallesPedido = detallesPedido;
    }
    public void addDetallesPedido(Stock producto, Integer cantidad){
        if (producto.getCantidad() >= cantidad) {
            producto.restarCantidad(cantidad);

            if(detallesPedido.containsKey(producto)){
                detallesPedido.put(producto, detallesPedido.get(producto) + cantidad);
            }else{
                detallesPedido.put(producto, cantidad);
            }
            System.out.println("Aumentado : " + cantidad + " unidades de " + producto.getNombre());
        }else{
            System.out.println("No hay suficiente stock de " + producto.getNombre() + " para hacer el pedido.");
        }
    }
    public void setFecha(Date fecha){
        this.fecha = fecha;
    }

    @Override
    public String toString() {
        return "\nPedido{" +
                " \n    Id=" + id +
                " \n    Cliente=" + cliente +
                " \n    DetallesPedido=" + detallesPedido +
                " \n    Fecha=" + fecha +
                "\n}";
    }
}
