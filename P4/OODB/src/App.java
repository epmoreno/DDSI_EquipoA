import javax.persistence.*;
import java.util.ArrayList;
import java.util.List;

public class App {

    public boolean inicializarPersonas(EntityManager em){
        try{
            Persona p1 = new Persona("Juan", "Perez", 30);
            Persona p2 = new Persona("Ana", "Ojeda", 20);
            
            TypedQuery<Persona> queryPersonas_check = em.createQuery("SELECT p FROM Persona p", Persona.class);
            List<Persona> personas_check = queryPersonas_check.getResultList();
            
            if(personas_check.size() == 0){
                em.getTransaction().begin();
                em.persist(p1);
                em.persist(p2);
                em.getTransaction().commit();
            }
            
            return true;
        }catch(Exception e){
            System.out.println("Error al crear las personas: " + e.getMessage());
            return false;
        }
    }

    public boolean inicializarStocks(EntityManager em){
        try{
            ArrayList<Stock> huerta = new ArrayList<Stock>();
            huerta.add(new Stock("Lechugas", 100));
            huerta.add(new Stock("Tomates", 100));  
            huerta.add(new Stock("Cebollas", 100));
            huerta.add(new Stock("Ajos", 100));
            huerta.add(new Stock("Pimientos", 100));
            huerta.add(new Stock("Manzanas", 100));
            huerta.add(new Stock("Zanahorias", 100));
            huerta.add(new Stock("Patatas", 100));
            huerta.add(new Stock("Calabacines", 100));
            huerta.add(new Stock("Berenjenas", 100));
            huerta.add(new Stock("Pepinos", 100));
            
            TypedQuery<Stock> queryStock_check = em.createQuery("SELECT s FROM Stock s", Stock.class);
            List<Stock> stocks_check = queryStock_check.getResultList();
            if (stocks_check.size() == 0) {
                try{
                    em.getTransaction().begin();
                    for (Stock stock : huerta) {
                        em.persist(stock);
                    }
                    em.getTransaction().commit();
                }catch(Exception e){
                    System.out.println("Error al crear los stocks: " + e.getMessage());
                }
            }
            return true;
        }catch(Exception e){
            System.out.println("Error al crear los stocks: " + e.getMessage());
            return false;
        }
    }
    
    public boolean inicializarPedidos(EntityManager em, Persona cliente, Stock detallesPedido, Integer cantidad){
        try{
            TypedQuery<Pedido> queryPedido_check = em.createQuery("SELECT o FROM Pedido o WHERE o.cliente = :cliente", Pedido.class);
            queryPedido_check.setParameter("cliente", cliente);
            List<Pedido> pedidos_check = queryPedido_check.getResultList();
            
            if (pedidos_check.size() == 0){
                Pedido pedido = new Pedido(cliente);
                pedido.addDetallesPedido(detallesPedido, cantidad);
                em.getTransaction().begin();
                em.persist(pedido);
                em.getTransaction().commit();
            }else{
                Pedido pedidoExistente = pedidos_check.get(0);
                pedidoExistente.addDetallesPedido(detallesPedido, cantidad);
                em.getTransaction().begin();
                em.merge(pedidoExistente);
                em.getTransaction().commit();
            }
            return true;
        }catch(Exception e){
            System.out.println("Error al hacer el pedido : " + e.getMessage());
            return false;
        }
    }
    
    public void mostrarContenido(TypedQuery<?> query){
        List<?> results = query.getResultList();
        for (Object obj : results) {
            System.out.println(obj);
        }
    }

    public static void main(String[] args) throws Exception {
        EntityManagerFactory emf = Persistence.createEntityManagerFactory("objectdb:oodb.odb");
        EntityManager em = emf.createEntityManager();
        App app = new App();

        System.out.println("----- CREACION DE PERSONAS -----");
        if (app.inicializarPersonas(em))
            {System.out.println("Personas Guardadas con Exito!!\n");}
        TypedQuery<Persona> query = em.createQuery("SELECT p FROM Persona p", Persona.class);
        app.mostrarContenido(query);

        System.out.println("\n----- CREACION DE STOCKS -----");
        if(app.inicializarStocks(em))
            {System.out.println("Stocks Guardados con Exito!!\n");}
        TypedQuery<Stock> queryStock = em.createQuery("SELECT s FROM Stock s", Stock.class);
        app.mostrarContenido(queryStock);

        System.out.println("\n----- CREACION DE PEDIDOS -----");

        Persona cliente = query.getResultList().get(0);
        Stock articulo1 = queryStock.getResultList().get(0);
        if(app.inicializarPedidos(em, cliente, articulo1, 5))
            {System.out.println("Se ha hecho el pedido de: "+articulo1.getNombre()+" con Exito!!. CLiente : "+cliente.getNombre()+" Cantidad: 5\n");}
        if(app.inicializarPedidos(em, cliente, articulo1, 20))
            {System.out.println("Se ha hecho el pedido de: "+articulo1.getNombre()+" con Exito!!. CLiente : "+cliente.getNombre()+" Cantidad: 20\n");}
        
        Persona cliente2 = query.getResultList().get(1);
        Stock articulo1_2 = queryStock.getResultList().get(2);
        Stock articulo2_2 = queryStock.getResultList().get(3);
        if(app.inicializarPedidos(em, cliente2, articulo1_2, 15))
            {System.out.println("Se ha hecho el pedido de: "+articulo1_2.getNombre()+" con Exito!!. CLiente : "+cliente2.getNombre()+" Cantidad: 5\n");}
        if(app.inicializarPedidos(em, cliente2, articulo2_2, 13))
            {System.out.println("Se ha hecho el pedido de: "+articulo2_2.getNombre()+" con Exito!!. CLiente : "+cliente2.getNombre()+" Cantidad: 20\n");}
        
        TypedQuery<Pedido> queryPedido = em.createQuery("SELECT o FROM Pedido o", Pedido.class);
        app.mostrarContenido(queryPedido);

        em.close();
        emf.close();
    }

}
